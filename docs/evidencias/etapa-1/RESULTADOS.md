# Resultado G1 para revisión

Estado: implementación preparada; aceptación humana PENDIENTE.

- Fuentes oficiales: seis ZIP INE; 2,999,641 filas agregadas originales de Jalisco validadas, sin duplicados de clave ni descartes.
- Resultado: 750 registros (125 municipios x seis elecciones). Conservación LN=SV+NV+NS. Continuidad exacta de claves/nombres, sin afirmar equivalencia geométrica.
- Train final: 2015, 2018 y 2021; n=375. Validación previa: 2021 (train 2015/2018), n=125. Test final: 2024, n=125.
- Random Forest test: MAE=3.2418158186 pp, RMSE=4.1634845087 pp.
- Baseline comparable 2018: MAE=3.9801046016 pp, RMSE=5.2258361570 pp.
- Estrategia elegida con validación 2021: random_forest. No seleccionada por test final.
- 19 pruebas locales aprobadas; instalación independiente con dependencias fijadas, hashes y pip check aprobados. Reconstrucción independiente desde caché y descargas oficiales nuevas: nueve artefactos de datos/modelo idénticos SHA256.
- Hashes fijados para 22 archivos: datos/modelo, contrato, fuentes, diccionario, ejemplos y requirements.

## Límites que deben permanecer visibles

El objetivo es la abstención entre registros con condición conocida. NS no equivale a abstención. Los conteos de los cuadernillos excluyen casillas especiales y voto exterior. Las claves son INE, no INEGI. La cartografía es retrospectiva y no se entrega geometría homologada. Estimaciones solo como backtest 2024, interval=null. Una prueba temporal no garantiza precisión futura ni causalidad.

## Contrato

OpenAPI 3.0.3, API 1.1.0; ocho endpoints propuestos con ejemplos validados. Cambio antes de construir consumidores: agrega catálogo de elecciones, conteos/NS, claves, fechas y metadatos de backtest. Propuesta congelada por hash para revisión de Lluvia. No se implementó la API ni siguientes etapas.

## Evidencia

- pytest.txt: salida real de pruebas.
- environment.json: Python, versiones y fecha de ejecución.
- data_validation.json: conservación, conteos y anomalías de edad preservadas.
- reproducibility.json: reconstrucción con caché verificada.
- fresh_download_reproducibility.json y fresh_download_log.txt: reconstrucción desde nuevas descargas.
- clean_environment.json: instalación aislada, hashes, pruebas y pip check.
- contracts/CONTRACT_STATUS.json: versión y hash, aceptación pendiente.
