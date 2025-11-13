import ftplib
import io
import csv
from collections import Counter
import os

# ========================
# CONFIGURAZIONE FTP
# ========================
FTP_HOST = "ftp.andreat257.sg-host.com"
FTP_USER = "admin@andreat257.sg-host.com"

# Puoi scegliere:
# - mettere direttamente la password qui
# - oppure usare una variabile d'ambiente FTP_PASS su Render
FTP_PASS = os.environ.get("FTP_PASS", "1z$*j236|*db")

REMOTE_DIR = "/public_html/IMPORT_DATI_FULL_20230919_0940"
REMOTE_INPUT_FILE = "ARTICOLI.CSV"
REMOTE_OUTPUT_FILE = "ARTICOLI_REV.CSV"

# Se vuoi caricare il file generato di nuovo su FTP
UPLOAD_RESULT = True

# Delimitatore del CSV: spesso è ';' per i gestionali italiani
CSV_DELIMITER = ';'
# Encoding principale, con fallback a latin-1 in caso di problemi
CSV_ENCODING = "utf-8-sig"

# Nomi delle colonne così come sono scritti nel file CSV
CSV_COL_TITOLO = "TITOLO"
CSV_COL_FORMATO = "FORMATO"
CSV_COL_UM_FORMATO = "UM_FORMATO"


def download_csv_from_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.cwd(REMOTE_DIR)

    buffer = io.BytesIO()
    ftp.retrbinary(f"RETR {REMOTE_INPUT_FILE}", buffer.write)
    ftp.quit()

    buffer.seek(0)
    raw = buffer.read()

    # Provo prima con l'encoding principale
    try:
        text = raw.decode(CSV_ENCODING)
    except UnicodeDecodeError:
        # Fallback tipico per file da gestionali italiani (accenti ecc.)
        print(f"Decoding con '{CSV_ENCODING}' fallito, provo con 'latin-1'...")
        text = raw.decode("latin-1")

    return text


def process_csv(csv_text):
    # Leggo il CSV come lista di dict
    input_io = io.StringIO(csv_text)
    reader = csv.DictReader(input_io, delimiter=CSV_DELIMITER)

    rows = list(reader)
    fieldnames = reader.fieldnames

    if fieldnames is None:
        raise ValueError("Impossibile determinare le intestazioni del CSV (fieldnames è None).")

    # DEBUG: stampa le intestazioni trovate nel file
    print("Intestazioni CSV trovate:", fieldnames)

    # Verifica che le colonne configurate esistano
    required_cols = {
        "Titolo": CSV_COL_TITOLO,
        "Formato": CSV_COL_FORMATO,
        "Um_Formato": CSV_COL_UM_FORMATO,
    }

    for logical_name, real_name in required_cols.items():
        if real_name not in fieldnames:
            raise ValueError(
                f"Manca la colonna obbligatoria '{real_name}' (configurata per il campo logico '{logical_name}') nel CSV."
            )

    # Conta quante volte compare ogni titolo (usiamo la colonna reale)
    counts = Counter((row.get(CSV_COL_TITOLO) or "").strip() for row in rows)

    # Modifica solo i Titolo duplicati
    for row in rows:
        titolo = (row.get(CSV_COL_TITOLO) or "").strip()
        if counts[titolo] > 1:
            formato = (row.get(CSV_COL_FORMATO) or "").strip()
            um_formato = (row.get(CSV_COL_UM_FORMATO) or "").strip()

            parts = [titolo]
            if formato:
                parts.append(formato)
            if um_formato:
                parts.append(um_formato)

            # 🔴 ATTENZIONE: qui usiamo le variabili minuscole, NON FORMATO/UM_FORMATO maiuscole
            row[CSV_COL_TITOLO] = " ".join(parts)

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

    data = csv_text.encode("latin-1")  # salviamo in latin-1 per compatibilità con il gestionale
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
    with open(local_filename, "w", encoding="latin-1", newline='') as f:
        f.write(new_csv)
    print(f"File generato localmente: {local_filename}")

    if UPLOAD_RESULT:
        print("Carico ARTICOLI_REV.CSV su FTP...")
        upload_csv_to_ftp(new_csv)
        print("Upload completato.")

    print("Operazione terminata.")


if __name__ == "__main__":
    main()
