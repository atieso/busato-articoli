import ftplib
import io
import csv
from collections import Counter

# ========================
# CONFIGURAZIONE FTP
# ========================
FTP_HOST = "ftp.andreat257.sg-host.com"
FTP_USER = "admin@andreat257.sg-host.com"
FTP_PASS = "1z$*j236|*db"

REMOTE_DIR = "/public_html/IMPORT_DATI_FULL_20230919_0940"
REMOTE_INPUT_FILE = "ARTICOLI.CSV"
REMOTE_OUTPUT_FILE = "ARTICOLI_REV.CSV"

# Se vuoi caricare il file generato di nuovo su FTP
UPLOAD_RESULT = True

# Delimitatore del CSV: spesso è ';' per i gestionali italiani
CSV_DELIMITER = ';'   # cambia in ',' se necessario
CSV_ENCODING = "latin-1"


def download_csv_from_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(REMOTE_DIR)

    buffer = io.BytesIO()
    ftp.retrbinary(f"RETR {REMOTE_INPUT_FILE}", buffer.write)
    ftp.quit()

    buffer.seek(0)
    text = buffer.read().decode(CSV_ENCODING)
    return text


def process_csv(csv_text):
    # Leggo il CSV come lista di dict
    input_io = io.StringIO(csv_text)
    reader = csv.DictReader(input_io, delimiter=CSV_DELIMITER)

    rows = list(reader)
    fieldnames = reader.fieldnames

    if fieldnames is None:
        raise ValueError("Impossibile determinare le intestazioni del CSV (fieldnames è None).")

    # Verifica colonne necessarie
    required_cols = ["Titolo", "Formato", "Um_Formato"]
    for col in required_cols:
        if col not in fieldnames:
            raise ValueError(f"Manca la colonna obbligatoria '{col}' nel CSV.")

    # Conta quante volte compare ogni titolo
    counts = Counter(row["Titolo"] for row in rows)

    # Modifica solo i Titolo duplicati
    for row in rows:
        titolo = (row.get("Titolo") or "").strip()
        if counts[titolo] > 1:
            formato = (row.get("Formato") or "").strip()
            um_formato = (row.get("Um_Formato") or "").strip()

            parts = [titolo]
            if formato:
                parts.append(formato)
            if um_formato:
                parts.append(um_formato)

            row["Titolo"] = " ".join(parts)

    # Scrivo il nuovo CSV in memoria
    output_io = io.StringIO()
    writer = csv.DictWriter(output_io, fieldnames=fieldnames, delimiter=CSV_DELIMITER, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

    return output_io.getvalue()


def upload_csv_to_ftp(csv_text):
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(REMOTE_DIR)

    data = csv_text.encode(CSV_ENCODING)
    buffer = io.BytesIO(data)

    ftp.storbinary(f"STOR {REMOTE_OUTPUT_FILE}", buffer)
    ftp.quit()


def main():
    print("Scarico il file ARTICOLI.CSV da FTP...")
    original_csv = download_csv_from_ftp()

    print("Elaboro il CSV (rilevo duplicati su Titolo e concateno Formato / Um_Formato)...")
    new_csv = process_csv(original_csv)

    # Salva sempre una copia locale
    local_filename = "ARTICOLI_REV.CSV"
    with open(local_filename, "w", encoding=CSV_ENCODING, newline='') as f:
        f.write(new_csv)
    print(f"File generato localmente: {local_filename}")

    if UPLOAD_RESULT:
        print("Carico ARTICOLI_REV.CSV su FTP...")
        upload_csv_to_ftp(new_csv)
        print("Upload completato.")

    print("Operazione terminata.")


if __name__ == "__main__":
    main()
