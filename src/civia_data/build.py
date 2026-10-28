"""Read official aggregate rows, validate and sum to INE municipalities."""
import argparse
import io
import json
import unicodedata
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from civia_data.common import ROOT, YEARS, DATES, sha256, write_json

KEY = ["AELEC", "EDOCVE", "MPIOCVE", "SECCION", "SEXO", "EDAD"]
COUNTS = ["LN", "SV", "NV", "NS"]
COLUMNS = KEY + ["FELECCION", "EDONOM", "MPIONOM"] + COUNTS


def validate_raw(frame, year):
    if frame.empty or frame[COLUMNS].isna().any().any() or frame[COLUMNS].eq("").any().any():
        raise ValueError("CSV vacío o faltantes en columnas obligatorias")
    numbers = KEY + COUNTS
    for column in numbers:
        values = pd.to_numeric(frame[column], errors="raise")
        if not np.isfinite(values).all() or (values % 1 != 0).any():
            raise ValueError(f"No entero: {column}")
        frame[column] = values.astype("int64")
    if not frame.AELEC.eq(year).all() or not frame.EDOCVE.eq(14).all():
        raise ValueError("Año o entidad no coincide con el alcance")
    if frame.duplicated(KEY).any():
        raise ValueError("Filas agregadas duplicadas; no deduplicar ni sumar a ciegas")
    if (frame[COUNTS] < 0).any().any() or not frame.LN.eq(frame.SV + frame.NV + frame.NS).all():
        raise ValueError("Conteos negativos o LN != SV+NV+NS")
    if not frame.MPIOCVE.between(1, 125).all():
        raise ValueError("Clave municipal fuera de cobertura")
    if not frame.SEXO.isin([0, 1, 2]).all() or not frame.EDAD.ge(18).all():
        raise ValueError("Sexo/edad agregada fuera de dominio")
    # 2024 source explicitly contains mm/dd/yyyy, not day/month.
    expected_raw = {2009: "5/7/2009", 2012: "1/7/2012", 2015: "7/6/2015", 2018: "1/7/2018", 2021: "6/6/2021", 2024: "06/02/2024"}
    if not frame.FELECCION.eq(expected_raw[year]).all():
        raise ValueError("Formato/fecha oficial inesperada: revisar sin inferir día/mes")
    return frame


def aggregate(frame, year):
    frame = validate_raw(frame.copy(), year)
    names = frame.groupby("MPIOCVE").MPIONOM.nunique()
    if names.gt(1).any():
        raise ValueError("Una clave tiene nombres contradictorios")
    grouped = frame.groupby("MPIOCVE", sort=True)[COUNTS].sum().reset_index()
    grouped["territory_id"] = "14" + grouped.MPIOCVE.astype(str).str.zfill(3)
    grouped["territory_name"] = grouped.MPIOCVE.map(frame.groupby("MPIOCVE").MPIONOM.first())
    grouped["known_count"] = grouped.SV + grouped.NV
    if (grouped.known_count <= 0).any():
        raise ValueError("Sin denominador conocido; no generar porcentaje")
    grouped["participation_pct"] = 100 * grouped.SV / grouped.known_count
    grouped["abstention_pct"] = 100 - grouped.participation_pct
    grouped["unknown_pct"] = 100 * grouped.NS / grouped.LN
    grouped["participation_lower_pct"] = 100 * grouped.SV / grouped.LN
    grouped["participation_upper_pct"] = 100 * (grouped.SV + grouped.NS) / grouped.LN
    grouped["election_id"] = f"federal-{year}"
    grouped["year"] = year
    grouped["election_date"] = DATES[year]
    grouped["election_type"] = "federal_concurrente" if year in (2012, 2018, 2024) else "federal_intermedia"
    grouped["source_id"] = f"ine-ccpc-{year}-jal"
    grouped["data_status"] = "observado"
    grouped["denominator"] = "SV+NV"
    return grouped.drop(columns="MPIOCVE").rename(columns={"LN": "nominal_count", "SV": "voted_count", "NV": "not_voted_count", "NS": "unknown_count"})


def build(root=ROOT):
    root = Path(root)
    sources = json.loads((root / "data/sources.lock.json").read_text(encoding="utf-8"))
    frames, reports = [], []
    for source in sorted(sources, key=lambda x: x["year"]):
        year = source["year"]
        path = root / f"data/raw/ine_{year}.zip"
        if sha256(path) != source["sha256"]:
            raise ValueError(f"Hash de fuente incorrecto {year}")
        with ZipFile(path) as archive:
            csv = archive.read(source["member"])
        if __import__("hashlib").sha256(csv).hexdigest() != source["member_sha256"]:
            raise ValueError("Hash de CSV interno incorrecto")
        raw = pd.read_csv(io.BytesIO(csv), encoding="utf-8-sig", dtype=str, usecols=COLUMNS, keep_default_na=False)
        if raw.eq("").any().any():
            raise ValueError("Campos obligatorios vacíos")
        municipal = aggregate(raw, year)
        frames.append(municipal)
        reports.append({"year": year, "input_rows": len(raw), "output_municipalities": len(municipal), "discarded_rows": 0, "missing_required": 0, "duplicate_keys": 0, "source_rows_age_over_120_preserved": int(pd.to_numeric(raw.EDAD).gt(120).sum()), "unknown_count": int(municipal.unknown_count.sum()), "nominal_count": int(municipal.nominal_count.sum())})
    result = pd.concat(frames, ignore_index=True).sort_values(["territory_id", "year"]).reset_index(drop=True)
    if set(result.year) != set(YEARS) or result.duplicated(["territory_id", "election_id"]).any():
        raise ValueError("Panel incompleto o duplicado")
    first = None
    for year, group in result.groupby("year"):
        current = dict(zip(group.territory_id, group.territory_name))
        if first is not None and current != first:
            raise ValueError("Cambios de claves/nombres: requiere tabla de correspondencia revisada")
        first = current
    out = root / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    csvpath = out / "participation.csv"
    result.to_csv(csvpath, index=False, float_format="%.10f", lineterminator="\n")
    version = "ine-ccpc-jal-" + sha256(csvpath)[:12]
    territories = result[result.year.eq(2024)][["territory_id", "territory_name"]].rename(columns={"territory_id": "id", "territory_name": "name"})
    territories["level"] = "municipio"
    territories["state_id"] = "14"
    territories["code_system"] = "INE_EDOCVE_MPIOCVE"
    write_json(out / "territories.json", territories.to_dict("records"))
    write_json(out / "elections.json", result[["election_id", "year", "election_date", "election_type"]].drop_duplicates().sort_values("year").to_dict("records"))
    write_json(out / "metadata.json", {"source_version": version, "scope": "125 municipios INE de Jalisco", "territory_code_system": "INE_EDOCVE_MPIOCVE", "years": list(YEARS), "denominator": "SV+NV", "n_rows": len(result), "geometry_available": False, "warnings": ["No incluye casillas especiales ni voto exterior", "NS no equivale a abstención", "Porcentajes entre registros con condición de voto conocida", "No unir claves INE con INEGI sin correspondencia revisada", "Cartografía histórica retrospectiva: 2021 en archivos 2009-2021; 2023 en 2024; no se garantiza estabilidad de polígonos"]})
    write_json(root / "docs/evidencias/etapa-1/data_validation.json", {"rows": len(result), "sources": reports, "key_name_continuity": True, "geometry_equivalence_verified": False, "source_version": version})
    print(f"Tabla validada: {len(result)} filas; {version}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    build(parser.parse_args().root)
