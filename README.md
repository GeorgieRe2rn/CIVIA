# CIVIA

Repositorio compartido de Jorge, Lluvia, Lalo y Viviana. Analítica electoral agregada con web, app móvil y API compartida.

## Estado actual

`develop` contiene G1, G2 y G3 integradas mediante PR. G1 aporta el pipeline oficial del INE para 125 municipios de Jalisco, seis elecciones (2009-2024), el modelo retrospectivo, el contrato y sus pruebas. G2 aporta la API FastAPI, la ingesta idempotente, la persistencia local con SQLite y la migración PostgreSQL/PostGIS, validada en un contenedor local real. G3 se integró mediante PR #7 con merge squash `fec9404`; su check `verify` pasó.

La revisión GitHub separada de G3 no quedó registrada porque la cuenta autenticada era la autora del PR y GitHub bloquea la auto-revisión; la autorización explícita de Viviana queda documentada en el acta. G4 móvil está en desarrollo en `etapa/04-mobile-release`; el E2E web local pasa `3/3`, el workflow integral remoto pasó sus cinco jobs y el emulador Android fue probado contra la API. Aún requiere teléfono físico/LAN y revisión de Jorge.

## Qué hace cada persona

| Orden | Responsable | Trabajo | Revisor |
| --- | --- | --- | --- |
| 1 | Jorge | Datos, ML y contrato (G1) | Lluvia |
| 2 | Lluvia | Backend, API y seguridad (G2) | Lalo |
| 3 | Lalo | Web, mapas y escenarios (G3) | Viviana |
| 4 | Viviana | App Expo, integración y entrega (G4) | Jorge |

Una sola persona desarrolla a la vez. La siguiente comienza cuando el PR anterior esté integrado y el acta sea ACEPTADA por su revisor humano. La preparación inicial del repositorio no aprueba G1. Meta de entrega del equipo: 31 de octubre de 2026; confirmar por separado el plazo oficial.

## Cómo comenzar

1. Jorge invita a los otros tres como colaboradores desde Settings > Collaborators y confirma sus cuentas. Esta configuración no se ha realizado automáticamente.
2. Cada integrante clona este repositorio una sola vez: `git clone https://github.com/GeorgieRe2rn/CIVIA.git`.
3. Lee la guía PDF personal del paquete entregado y `docs/COMO_TRABAJAMOS.md` en este repositorio.
4. Cambiar a `develop` actualizado y crear la rama propia desde ahí. Jorge inicia en `etapa/01-datos-ml`; los demás esperan el relevo aceptado. Cada etapa hace PR hacia `develop`, nunca directamente hacia `main`.
5. Para usar una IA, adjunta tu guía de apoyo y dale acceso a este repositorio; pídele que lea contrato y acta anterior antes de modificar archivos.

## Para qué sirven los archivos de apoyo

No existe una carpeta kit_github que deban instalar. Los archivos ya están en su ubicación de trabajo:

| Archivo | Uso |
| --- | --- |
| `contracts/openapi.yaml` | Contrato propuesto de API. Jorge lo congela en G1; Lluvia lo implementa; web y móvil lo consumen. Es JSON válido, compatible con YAML. |
| `.github/ISSUE_TEMPLATE/tarea.md` | GitHub lo ofrece al crear una tarea desde Issues > New issue. |
| `.github/PULL_REQUEST_TEMPLATE.md` | GitHub lo inserta al abrir un PR para revisión. |
| `docs/ACTA_RELEVO.md` | Plantilla de entrega de etapa. |
| `docs/relevos/` | Un acta por persona, inicialmente PENDIENTE. |
| `.gitignore` | Evita incorporar secretos, dependencias y archivos locales. |
| `.env.example` | Lista de variables sin claves; copiar a `.env` local al implementar y completar solo en el equipo. |

`services/api` contiene la implementación G2 y su README de arranque. `apps/web` contiene la implementación G3 integrada y su evidencia; `apps/mobile` contiene el cliente Expo en desarrollo y su guía de LAN. `data`, `ml`, `src/civia_data`, `tests` y `scripts` contienen G1 y las pruebas/scripts de API.

## Seguridad y alcance

No publicar claves ni datos personales. Cifras de mockups son ficticias; datos reales con fuentes y versiones. Separar observado, predicho y simulado. Gemini apagado por defecto, opcional y sin facturación. No predicción individual ni persuasión partidista. Ante un defecto previo, pausar etapa activa, corregir con su autor, revisar y reanudar sin trabajo simultáneo.

## API G2 local

Con Python 3.12 y `requirements.lock` instalado, la API usa SQLite local cuando `DATABASE_URL` está vacío:

```powershell
uvicorn app.main:app --app-dir services/api --reload
```

Para PostgreSQL/PostGIS, ejecutar `python scripts/migrate_api.py`, después `python scripts/ingest_api.py` y arrancar Uvicorn. Ver [services/api/README.md](services/api/README.md). La ruta fue validada localmente; la geometría permanece no disponible hasta contar con correspondencia documentada.

## Revisión y protección

Trabajar mediante ramas y PR: rama de etapa → develop; release validada: develop → main. Sin push directo ni force push a develop o main después de la creación inicial de develop. Configurar protección de ambas ramas, aprobación humana y verificaciones cuando permisos y plan lo permitan. Protección no configurada. `.github/workflows/g1.yml` verifica hashes, contrato y tests sobre Windows/Python 3.12; `.github/workflows/integral.yml` cubre API, PostGIS, web, móvil y E2E. El resultado remoto debe consultarse en Actions; la existencia del workflow no significa ejecución aprobada.

## Flujo GitHub explicado

`develop` es integración; `main` es entrega estable. Push sube cambios a TU rama. PR solicita revisión e integración. Merge incorpora un PR aprobado. Leer el tutorial completo en [docs/COMO_TRABAJAMOS.md](docs/COMO_TRABAJAMOS.md), con ejemplos por persona, botones de GitHub y relevo. El desarrollo se lee en [develop](https://github.com/GeorgieRe2rn/CIVIA/tree/develop).

## Ejecutar G1 desde un clon limpio (Windows)

Requisito: Python 3.12 de 64 bits y Git. Desde la raíz, ejecutar cada comando por separado y detenerse si falla:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe -m civia_data.verify
.\.venv\Scripts\python.exe -m pytest -q
```

Si el equipo no tiene el lanzador `py`, usar la ruta a su ejecutable Python 3.12 para el primer comando. No es necesario activar el entorno. Los demás comandos usan explícitamente `.venv`. En macOS/Linux, crear entorno con `python3.12 -m venv .venv` y sustituir `.venv/Scripts/python.exe` por `.venv/bin/python`.

Los datos agregados y artefactos pequeños están incluidos. Para reconstruirlos desde las seis descargas oficiales (aprox. 294 MB comprimidos, espacio adicional en disco):

```powershell
.\.venv\Scripts\python.exe -m civia_data.download
.\.venv\Scripts\python.exe -m civia_data.build
.\.venv\Scripts\python.exe -m civia_data.train
.\.venv\Scripts\python.exe -m civia_data.verify
.\.venv\Scripts\python.exe scripts/reproduce_check.py --from-cache
```

Para comprobar con descargas nuevas, ejecutar `python scripts/reproduce_check.py` usando el Python del entorno. No se modifica ni acepta una nueva fuente silenciosamente: si cambia un hash, revisar antes de regenerar el lock. Ver `scripts/README.md` para runner con parada automática.

## Resultado y límites G1

750 filas agregadas; entrenamiento en 2015/2018/2021, prueba 2024, 125 municipios. RF MAE **3.2418 pp**, baseline de elección comparable 2018 **3.9801 pp**. Estrategia elegida previamente con validación 2021. Ver `ml/artifacts/evaluation.json` para RMSE, tamaños y parámetros.

La tasa usa **SV/(SV+NV)**; NS se informa por separado, no como abstención. Claves son **INE**, no INEGI: Guadalajara **14041**. Solo se sirve backtest retrospectivo 2024, no pronósticos futuros. `interval=null` y no hay geometría verificada. Los resultados no prueban causalidad ni generalización a otras elecciones.

Entrega: [docs/ENTREGA_LLUVIA_G1.md](docs/ENTREGA_LLUVIA_G1.md), [metodología](docs/METODOLOGIA_G1.md), [diccionario/fuentes](data/README.md) y las actas en [docs/relevos](docs/relevos). El contrato interno 1.1.0 tiene ocho endpoints y es consumido por la API G2, la web G3 y el cliente móvil G4. La API se ha probado con SQLite y PostgreSQL/PostGIS real; el E2E web local pasa `3/3`, CI remoto pasa sus cinco jobs y el emulador Android carga datos reales, mientras geometría verificada, teléfono físico/LAN y aceptación G4 siguen pendientes.
