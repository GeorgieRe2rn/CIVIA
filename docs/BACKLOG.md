# Tablero inicial secuencial

Estados: Listo → En desarrollo → Revisión → Pruebas → Terminado. Una tarea termina solo con revisión/evidencia, nunca por generación de archivos.

| Tarea | Dueño | Dependencia | Aceptación | Evidencia | Estado |
|---|---|---|---|---|---|
| G1-01 Inventario/fuentes | Jorge | Inicio | URLs oficiales, fechas, hashes, alcance | data/sources.lock.json | Revisión |
| G1-02 Pipeline/diccionario | Jorge | G1-01 | 750 filas, tipos, cuentas, claves continuas | data/processed, data/dictionary.csv, data_validation.json | Revisión |
| G1-03 Baseline/modelo | Jorge | G1-02 | Partición temporal, MAE/RMSE reales, interval=null | ml/artifacts/evaluation.json, errors_by_municipality.csv | Revisión |
| G1-04 Contrato y relevo | Jorge | G1-03 | OpenAPI y ejemplos válidos, reproducción, acta | contracts, tests, docs/evidencias | Revisión |
| G2 API y PostgreSQL | Lluvia | G1 aceptada e integrada | Endpoints, persistencia y validaciones | Pendiente | Backlog |
| G3 Web | Lalo | G2 aceptada e integrada | Flujos reales, accesibilidad y build | Pendiente | Backlog |
| G4 Expo/integración/release | Viviana | G3 aceptada e integrada | Dispositivo físico, E2E y PR develop→main | Pendiente | Backlog |

Jorge confirma disponibilidad y fecha real de relevo; las ventanas del plan inicial eran propuestas, no horas trabajadas. Mantener como meta del equipo 31 de octubre de 2026, verificando hora/canal oficiales.
