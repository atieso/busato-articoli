# Script ARTICOLI_REV - Gestione Titoli Duplicati su ARTICOLI.CSV

Questo script legge il file `ARTICOLI.CSV` da un server FTP, cerca i duplicati sulla colonna **Titolo** e,
solo per i titoli duplicati, concatena `Titolo + Formato + Um_Formato` nella stessa colonna **Titolo**.

Infine genera un nuovo file `ARTICOLI_REV.CSV` (localmente e, opzionalmente, lo carica di nuovo su FTP).

---

## Requisiti

- Python 3.9+ (o versione compatibile)
- Nessuna libreria esterna: usa solo la libreria standard di Python.

File principali:

- `genera_articoli_rev.py` → script principale
- `requirements.txt` → vuoto (nessuna dipendenza esterna)
- `render.yaml` → configurazione per job cron su Render

---

## Configurazione

Nel file `genera_articoli_rev.py`:

- Imposta i parametri FTP:

```python
FTP_HOST = "ftp.andreat257.sg-host.com"
FTP_USER = "admin@andreat257.sg-host.com"
FTP_PASS = "LA_TUA_PASSWORD_FTP"
REMOTE_DIR = "/public_html/IMPORT_DATI_FULL_20230919_0940"
REMOTE_INPUT_FILE = "ARTICOLI.CSV"
REMOTE_OUTPUT_FILE = "ARTICOLI_REV.CSV"
