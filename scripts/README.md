# Comandos G1

Ejecutar desde la raíz del repositorio después de instalar dependencias.

```powershell
.\.venv\Scripts\python.exe -m civia_data.download
.\.venv\Scripts\python.exe -m civia_data.build
.\.venv\Scripts\python.exe -m civia_data.train
.\.venv\Scripts\python.exe -m civia_data.verify
.\.venv\Scripts\python.exe -m pytest -q
```

Detenerse si falla un comando. Para ejecutar toda la secuencia con parada automática: `powershell -ExecutionPolicy Bypass -File scripts/run_g1.ps1`. El bypass afecta solo esa ejecución local del script revisable, no la política permanente del sistema.

Reconstrucción completamente independiente desde nuevas descargas: `python scripts/reproduce_check.py`. Con bytes ya descargados y verificados: `python scripts/reproduce_check.py --from-cache`. Ambos comparan SHA256 de todos los artefactos de datos/modelo con la referencia guardada.

`freeze_contract.py` genera ejemplos desde datos reales y prepara la propuesta 1.1.0. Se ejecutó en G1; no ejecutarlo para alterar un contrato aceptado sin revisión. `python -m civia_data.verify --write` renueva el manifest SOLO al producir una nueva versión revisada: no usarlo para ocultar un hash incorrecto.

Para validar una base PostgreSQL/PostGIS fresca después de migrar e ingerir dos veces, usar `python scripts/verify_postgres.py` con `DATABASE_URL` configurada. Comprueba conteos, duplicados, geometría y los endpoints de la API; no crea geometría ficticia.
