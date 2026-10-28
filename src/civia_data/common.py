import hashlib
import json
from pathlib import Path

YEARS = (2009, 2012, 2015, 2018, 2021, 2024)
ROOT = Path(__file__).resolve().parents[2]
PAGE = "https://portal.ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/"
DATES = {2009: "2009-07-05", 2012: "2012-07-01", 2015: "2015-06-07", 2018: "2018-07-01", 2021: "2021-06-06", 2024: "2024-06-02"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def source_url(year):
    prefix = "2025/08" if year == 2024 else "2022/04"
    return f"https://portal.ine.mx/wp-content/uploads/{prefix}/DatosAbiertos_DECEyEC_ConteosCensales{year}.zip"
