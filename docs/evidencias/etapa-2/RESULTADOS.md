# Evidencia tecnica G2

Estado de acta: PENDIENTE. Esta evidencia no sustituye revision humana, PR ni
integracion en `develop`.

## Entorno

- `python --version` -> `Python 3.13.1`.
- Python 3.12 no esta instalado en el equipo; la especificacion del proyecto
  continua fijando `>=3.12,<3.13`.
- `python -m venv .venv` -> correcto.
- `\.venv\Scripts\python.exe -m pip install -r requirements.lock` -> correcto.

## Comandos ejecutados

```powershell
\.venv\Scripts\python.exe -m pytest -q
```

Resultado observado: `31 passed`.

```powershell
\.venv\Scripts\python.exe -m compileall -q services/api/app scripts
```

Resultado observado: codigo de salida 0, sin salida.

```powershell
$env:PYTHONPATH="services/api;src"; .\.venv\Scripts\python.exe -c "from app.main import app; print(len(app.routes)); print(app.title)"
```

Resultado observado: `12` rutas; `CIVIA API`.

```powershell
$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m civia_data.verify
```

Resultado observado: `22 artefactos verificados`.

```powershell
\.venv\Scripts\python.exe scripts/ingest_api.py
```

Resultado observado: `Ingesta G1 completada de forma idempotente: ine-ccpc-jal-b76f8fc46187`.

Se inicio Uvicorn real en un puerto local y se consulto:

- `/api/health`: `status=ok`, `ai_enabled=False`.
- `/api/participacion?territorio=14041`: `6` observaciones.
- `/openapi.json`: version `1.1.0`.

Con `DATABASE_URL=postgresql://127.0.0.1:65432/civia` y timeout de 2 segundos,
un servidor no disponible respondio `/api/health` con `200 degraded` y
`/api/territorios` con `503 DATA_UNAVAILABLE`; no se expuso un error interno.

## Cobertura

`tests/test_api.py` valida catalogos, seis observaciones reales, prediccion
2024, intervalo nulo, escenarios delta 0 y -20, validacion delta 21, mapa 503,
asistente determinista, errores 404/422, rate limit, CORS explicito y respuestas
contra los esquemas del OpenAPI congelado.

## No ejecutado

- `scripts/migrate_api.py`: NO EJECUTADO; no hay servidor PostgreSQL/PostGIS
  local disponible (`psql` no esta instalado y el daemon Docker no esta activo).
- Prueba con Python 3.12: NO EJECUTADA; el runtime no esta instalado.
- Prueba desde telefono/LAN: NO EJECUTADA; corresponde a integracion posterior.
- Commit, push, PR, merge y aceptacion: NO EJECUTADOS.
