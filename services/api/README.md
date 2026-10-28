# services/api

API G2 de CIVIA: FastAPI/Pydantic, persistencia SQLAlchemy y migracion
PostgreSQL/PostGIS. Los datos se cargan desde los artefactos versionados de G1;
no se generan cifras de demostracion.

## Arranque local sin PostgreSQL

Con Python 3.12 y el entorno instalado desde `requirements.lock`, la API usa
SQLite en `work/civia_api.db` cuando `DATABASE_URL` esta vacia. La primera
ejecucion crea las tablas y hace una ingesta idempotente de los datos incluidos:

```powershell
uvicorn app.main:app --app-dir services/api --reload
```

Tambien se puede ejecutar una ingesta explicita:

```powershell
python scripts/ingest_api.py
```

## PostgreSQL/PostGIS local

Configura `DATABASE_URL` en `.env` sin subir ese archivo. Primero aplica la
migracion y despues ejecuta la ingesta:

```powershell
python scripts/migrate_api.py
python scripts/ingest_api.py
uvicorn app.main:app --app-dir services/api
```

Se aceptan URLs `postgresql://...` y se normalizan al driver `psycopg`; la
extension PostGIS debe estar instalada en el servidor local.

La migracion crea `sources`, `territories`, `elections`, `participation`,
`model_versions` y `predictions`, con claves unicas para que la ingesta pueda
repetirse. La columna geografica queda vacia hasta contar con una
correspondencia documentada; `/api/mapa` responde 503 mientras tanto.

## Configuracion y limites

`CORS_ORIGINS` acepta una lista separada por comas y nunca se transforma en
`*`. `AI_ENABLED` permanece apagado y el endpoint de asistente usa el fallback
determinista. La API aplica limite de tamano de cuerpo y rate limit por proceso;
no confia en `X-Forwarded-For`. `DATABASE_CONNECT_TIMEOUT` evita que una base
caida bloquee indefinidamente el health check.

Consulta `contracts/openapi.yaml` para el contrato congelado y
`docs/ENTREGA_LLUVIA_G1.md` para las limitaciones de datos y modelo.
