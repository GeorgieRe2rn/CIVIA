# Acta de relevo
Estado: ACEPTADO
Etapa y compuerta: 2 / G2
Responsable: LLUVIA
Revisor: Lalo
Fecha, hora, America/Hermosillo: 28/10/2026, 02:29, America/Hermosillo

PR y SHA integrado:
PR: https://github.com/GeorgieRe2rn/CIVIA/pull/5
SHA integrado en develop: c1eff2a
SHA completo: c1eff2ae92809c190e1fad901c11a0be8ccb5410

Dataset, modelo, contrato y hashes:
- source_version: ine-ccpc-jal-b76f8fc46187
- Modelo: g1-ine-ccpc-jal-b76f8fc46187
- Contrato OpenAPI v1.1.0
- Hash de integración G1: b8bd5e7f960957f0174f320ef80234a7bcf2f79b

Archivos y comandos reproducibles:
- scripts/migrate_api.py
- scripts/ingest_api.py
- services/api/migrations/001_initial.sql
- tests/test_api.py

Comandos ejecutados:
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q services/api/app scripts
$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m civia_data.verify
.\.venv\Scripts\python.exe scripts/ingest_api.py

Pruebas, resultado y evidencia:
- Instalación completada correctamente.
- pip check sin dependencias rotas.
- Compilación de módulos completada.
- Ingesta ejecutada.
- Evidencia: docs/evidencias/etapa-2/RESULTADOS.md
- Integración completada mediante PR #5 hacia develop.

Criterios aprobados uno por uno:
- API FastAPI implementada.
- Validaciones y manejo uniforme de errores.
- Persistencia SQLAlchemy.
- Compatibilidad SQLite y PostgreSQL/PostGIS.
- Migración inicial creada.
- Scripts de migración e ingesta incluidos.
- OpenAPI actualizado a versión 1.1.0.
- Rate limiting implementado.
- CORS configurado.
- README actualizado.
- Evidencia adjunta.
- Pruebas locales ejecutadas.
- Integración en develop completada.

Limitaciones / bloqueos:
- PostgreSQL/PostGIS no ejecutado por falta de entorno disponible.
- Python 3.12 no disponible en el equipo; validación realizada con Python 3.13.1.
- IA generativa desactivada.
- No existe geometría validada; /api/mapa responde 503 DATA_UNAVAILABLE.

Cambios de alcance autorizados:
- Integración de la dependencia G1 autorizada directamente por Jorge.

Firma del responsable:
LLUVIA

Aceptación del revisor humano:
Lalo

Siguiente persona habilitada:
Lalo (G3 Web, mapa y escenarios)