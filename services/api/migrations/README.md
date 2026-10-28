# Migraciones API

`001_initial.sql` requiere PostgreSQL con la extension PostGIS instalada.
`scripts/migrate_api.py` aplica los archivos en orden y registra cada version
en `schema_migrations`. La ingesta de los artefactos G1 se realiza por separado
con `scripts/ingest_api.py` y puede repetirse sin duplicar claves.
