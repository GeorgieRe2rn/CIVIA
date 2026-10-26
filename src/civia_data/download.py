"""Verified downloads. Existing bytes must match the checked-in source lock."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

from civia_data.common import ROOT, YEARS, PAGE, sha256, source_url, write_json


def download(root=ROOT):
    root = Path(root)
    lockpath = root / "data/sources.lock.json"
    if not lockpath.exists():
        raise ValueError("Falta sources.lock.json; no aceptar silenciosamente nuevas versiones.")
    sources = json.loads(lockpath.read_text(encoding="utf-8"))
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    for record in sources:
        year = record["year"]
        if year not in YEARS or record["url"] != source_url(year):
            raise ValueError("Origen fuera de lista autorizada")
        path = raw / f"ine_{year}.zip"
        if not path.exists():
            temp = path.with_suffix(".part")
            try:
                with urlopen(record["url"], timeout=180) as response, temp.open("wb") as out:
                    for block in iter(lambda: response.read(1024 * 1024), b""):
                        out.write(block)
                if sha256(temp) != record["sha256"]:
                    raise ValueError(f"El INE cambió los bytes de {year}; revisar y versionar antes de continuar")
                temp.replace(path)
            finally:
                if temp.exists():
                    temp.unlink()
        if sha256(path) != record["sha256"]:
            raise ValueError(f"SHA256 incorrecto: {path}")
        with ZipFile(path) as archive:
            if record["member"] not in archive.namelist():
                raise ValueError("Falta CSV de Jalisco")
        print(f"Fuente verificada: {year}", flush=True)
    return sources


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    download(parser.parse_args().root)
