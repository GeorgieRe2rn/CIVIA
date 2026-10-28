# Acta de relevo
Estado: PENDIENTE
Etapa y compuerta: 2 / G2
Responsable: LLUVIA
Revisor: Lalo
Fecha, hora, America/Hermosillo: PENDIENTE
Destino de integracion: develop
PR y SHA integrado: PENDIENTE; no se ha creado commit ni PR
Dataset, modelo, contrato y hashes: source_version `ine-ccpc-jal-b76f8fc46187`; modelo `g1-ine-ccpc-jal-b76f8fc46187`; contrato 1.1.0; `22 artefactos verificados`
Archivos y comandos reproducibles: implementacion en `services/api/app`; migracion en `services/api/migrations/001_initial.sql`; scripts `scripts/migrate_api.py` y `scripts/ingest_api.py`; comandos y resultados en `docs/evidencias/etapa-2/RESULTADOS.md`
Pruebas, resultado y evidencia: `31 passed`; compilacion de API/scripts sin salida; Uvicorn real respondio health OK, `ai_enabled=False`, OpenAPI 1.1.0 y 6 observaciones; base no disponible respondio `degraded`/`503 DATA_UNAVAILABLE`; validacion de respuestas contra OpenAPI congelado incluida en `tests/test_api.py`
Criterios aprobados uno por uno:
- Ingesta idempotente y almacenamiento local SQLite: evidencia tecnica ejecutada; PostgreSQL/PostGIS: PENDIENTE
- Endpoints health, catalogos, participacion, predicciones, escenarios, mapa y asistente: evidencia tecnica ejecutada; revision humana PENDIENTE
- Errores 404/422/503, delta, rate limit, CORS explicito, IA apagada y ausencia de secretos: evidencia tecnica ejecutada; revision humana PENDIENTE
- Migracion PostgreSQL/PostGIS y prueba en servidor real: NO EJECUTADO
Limitaciones / bloqueos: el equipo local solo tiene Python 3.13.1, mientras el proyecto fija Python 3.12; `psql` no esta instalado y el daemon Docker no esta activo, por lo que PostgreSQL/PostGIS no se ejecuto. La API se verifico provisionalmente con el lock en Python 3.13. No hay geometria G1, por lo que `/api/mapa` responde 503.
Cambios de alcance autorizados: ninguno; SQLite es fallback local de prueba, no sustituye PostgreSQL/PostGIS para la compuerta.
Firma del responsable: PENDIENTE
Aceptacion del revisor humano: PENDIENTE; corresponde a Lalo
Siguiente persona habilitada: PENDIENTE hasta revision, PR integrado y aceptacion humana
No aceptar con fallas P0. No inventar evidencia.
