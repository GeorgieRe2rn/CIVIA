# Tablero inicial secuencial

Estados: Listo → En desarrollo → Revisión → Pruebas → Terminado. Una tarea termina solo con revisión/evidencia, nunca por generación de archivos.

| Tarea | Dueño | Dependencia | Aceptación | Evidencia | Estado |
|---|---|---|---|---|---|
| G1-01 Inventario/fuentes | Jorge | Inicio | URLs oficiales, fechas, hashes, alcance | data/sources.lock.json | Terminado por autorización de Jorge; PR #2 integrado |
| G1-02 Pipeline/diccionario | Jorge | G1-01 | 750 filas, tipos, cuentas, claves continuas | data/processed, data/dictionary.csv, data_validation.json | Terminado por autorización de Jorge; PR #2 integrado |
| G1-03 Baseline/modelo | Jorge | G1-02 | Partición temporal, MAE/RMSE reales, interval=null | ml/artifacts/evaluation.json, errors_by_municipality.csv | Terminado por autorización de Jorge; PR #2 integrado |
| G1-04 Contrato y relevo | Jorge | G1-03 | OpenAPI y ejemplos válidos, reproducción, acta | contracts, tests, docs/evidencias | Terminado por autorización de Jorge; PR #2 integrado |
| G2 API y PostgreSQL | Lluvia | G1 aceptada e integrada | Endpoints, persistencia y validaciones | docs/evidencias/etapa-2, docs/relevos/02_LLUVIA.md, docs/evidencias/etapa-3/RESULTADOS.md | Integrado en develop; acta aceptada. PostgreSQL/PostGIS validado localmente; geometría pendiente |
| G3 Web | Lalo | G2 aceptada e integrada | Flujos reales, accesibilidad y build | PR #7, docs/evidencias/etapa-3, docs/relevos/03_LALO.md | Integrado en develop por squash `fec9404`; verify pasó. GitHub no registra auto-revisión; autorización explícita documentada |
| G4 Expo/integración/release | Viviana | G3 aceptada e integrada | Dispositivo físico, E2E y PR develop→main | docs/relevos/04_VIVIANA.md, docs/evidencias/etapa-4/RESULTADOS.md | En desarrollo en `etapa/04-mobile-release`; Expo compila, E2E web local `3/3`, CI remoto `5/5` y emulador Android verificado; teléfono físico/LAN, PR G4 y geometría siguen pendientes |

Jorge confirma disponibilidad y fecha real de relevo; las ventanas del plan inicial eran propuestas, no horas trabajadas. Mantener como meta del equipo 31 de octubre de 2026, verificando hora/canal oficiales.
