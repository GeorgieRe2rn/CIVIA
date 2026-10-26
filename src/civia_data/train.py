"""Chronological municipal backtest. Fixed hyperparameters; no selection on test."""
import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from civia_data.common import ROOT, sha256, write_json

FEATURES = ["lag6_abstention_pct", "lag3_abstention_pct", "log_lag3_nominal", "lag3_unknown_pct", "is_concurrent"]
PARAMS = {"n_estimators": 200, "max_depth": 4, "min_samples_leaf": 10, "random_state": 42, "n_jobs": 1}


def features(history):
    if history.duplicated(["territory_id", "year"]).any():
        raise ValueError("Duplicado en historia")
    lookup = history.set_index(["territory_id", "year"])
    rows = []
    for row in history.sort_values(["year", "territory_id"]).itertuples():
        key3, key6 = (row.territory_id, row.year - 3), (row.territory_id, row.year - 6)
        if key3 not in lookup.index or key6 not in lookup.index:
            continue  # Initial 2009/2012 have no lag6: not fabricated or imputed.
        p3, p6 = lookup.loc[key3], lookup.loc[key6]
        if p6.election_type != row.election_type:
            raise ValueError("Baseline no comparable por tipo")
        rows.append({"territory_id": row.territory_id, "year": row.year, "feature_max_year": row.year - 3,
                     "election_id": row.election_id, "target": row.abstention_pct,
                     "lag6_abstention_pct": float(p6.abstention_pct), "lag3_abstention_pct": float(p3.abstention_pct),
                     "log_lag3_nominal": float(np.log1p(p3.nominal_count)), "lag3_unknown_pct": float(p3.unknown_pct),
                     "is_concurrent": int(row.election_type == "federal_concurrente")})
    result = pd.DataFrame(rows)
    if result.empty or not (result.feature_max_year < result.year).all():
        raise ValueError("Historia insuficiente o fuga temporal")
    return result


def split(frame, test_year):
    train = frame[frame.year < test_year].copy()
    test = frame[frame.year == test_year].copy()
    if train.empty or test.empty or train.year.max() >= test.year.min():
        raise ValueError("Partición temporal inválida")
    return train, test


def metrics(y, pred):
    return {"mae_pp": float(mean_absolute_error(y, pred)), "rmse_pp": float(root_mean_squared_error(y, pred)), "n": len(y)}


def train(root=ROOT):
    root = Path(root)
    history = pd.read_csv(root / "data/processed/participation.csv", dtype={"territory_id": str})
    panel = features(history)
    # Choose serving strategy using 2021 validation ONLY, before accessing 2024 labels for scoring.
    early, val = split(panel, 2021)
    validation_model = RandomForestRegressor(**PARAMS).fit(early[FEATURES], early.target)
    val_rf = metrics(val.target, validation_model.predict(val[FEATURES]))
    val_baseline = metrics(val.target, val.lag6_abstention_pct)
    strategy = "random_forest" if val_rf["mae_pp"] < val_baseline["mae_pp"] else "baseline_lag6"
    final_train, test = split(panel, 2024)
    model = RandomForestRegressor(**PARAMS).fit(final_train[FEATURES], final_train.target)
    rf_pred = np.clip(model.predict(test[FEATURES]), 0, 100)
    baseline = test.lag6_abstention_pct.to_numpy()
    rf_score, base_score = metrics(test.target, rf_pred), metrics(test.target, baseline)
    served = rf_pred if strategy == "random_forest" else baseline
    metadata = json.loads((root / "data/processed/metadata.json").read_text(encoding="utf-8"))
    version = "g1-" + metadata["source_version"]
    warnings = ["Backtest retrospectivo, no pronóstico validado de elecciones futuras", "Solo 125 municipios y una elección final de prueba; no equivale a 125 experimentos temporales independientes", "Sin intervalo: no hay bloque de calibración temporal independiente", "NS y cartografía retrospectiva limitan comparabilidad; no es inferencia causal"]
    if rf_score["mae_pp"] >= base_score["mae_pp"]:
        warnings.append("Random Forest no mejora el baseline en 2024; informar sin ocultarlo")
    if strategy == "baseline_lag6":
        warnings.append("Se sirve baseline por selección previa en validación 2021; no cambiarlo por mirar test 2024")
    report = {"model_version": version, "source_version": metadata["source_version"], "features": FEATURES, "params": PARAMS,
              "validation": {"train_years": sorted(early.year.unique().tolist()), "test_year": 2021, "random_forest": val_rf, "baseline": val_baseline},
              "selected_strategy": strategy, "selection_rule": "Menor MAE en validación 2021; nunca seleccionar por test 2024",
              "train_years": sorted(final_train.year.unique().tolist()), "test_year": 2024, "n_train": len(final_train), "n_test": len(test),
              "random_forest": rf_score, "baseline": base_score, "served": metrics(test.target, served), "interval": None, "warnings": warnings,
              "sklearn_version": sklearn.__version__, "dataset_sha256": sha256(root / "data/processed/participation.csv")}
    out = root / "ml/artifacts"
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "report": report}, out / "random_forest.joblib", compress=3)
    write_json(out / "evaluation.json", report)
    predictions = []
    for j, row in enumerate(test.itertuples()):
        predictions.append({"territory_id": row.territory_id, "election_id": row.election_id, "evaluation_mode": "retrospective_holdout",
                            "abstention_pct": float(served[j]), "participation_pct": float(100 - served[j]), "model_version": version,
                            "strategy": strategy, "mae_pp": report["served"]["mae_pp"], "baseline_mae_pp": base_score["mae_pp"],
                            "n_test": len(test), "interval": None, "warnings": warnings})
    write_json(out / "predictions_2024.json", predictions)
    errors = test[["territory_id", "election_id", "year", "target", "feature_max_year"]].copy()
    errors["rf_predicted"] = rf_pred
    errors["baseline_predicted"] = baseline
    errors["rf_absolute_error_pp"] = np.abs(test.target.to_numpy() - rf_pred)
    errors["baseline_absolute_error_pp"] = np.abs(test.target.to_numpy() - baseline)
    errors.to_csv(out / "errors_by_municipality.csv", index=False, float_format="%.10f", lineterminator="\n")
    panel.to_csv(out / "training_panel.csv", index=False, float_format="%.10f", lineterminator="\n")
    print(json.dumps({"n_train": len(final_train), "n_test": len(test), "strategy": strategy, "rf": rf_score, "baseline": base_score}, ensure_ascii=False))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    train(parser.parse_args().root)
