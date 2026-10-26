# Modelos G1

Entrenar: python -m civia_data.train

artifacts/evaluation.json contiene evaluación real, particiones, parámetros y advertencias. predictions_2024.json contiene únicamente backtest 2024. errors_by_municipality.csv contiene errores y baseline por municipio. training_panel.csv conserva trazabilidad de rezagos. random_forest.joblib es un artefacto propio para reproducción; no cargar joblib de fuentes no confiables. No hay pronóstico validado de elecciones futuras ni intervalo calibrado. Leer docs/METODOLOGIA_G1.md.
