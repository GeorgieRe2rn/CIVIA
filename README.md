# CIVIA

Repositorio compartido de Jorge, Lluvia, Lalo y Viviana. Analítica electoral agregada con web, app móvil y API compartida.

## Estado actual

Se incorporaron los archivos de coordinación y el contrato propuesto. La aplicación, base de datos y modelo todavía no están implementados en este repositorio. No hay pruebas de producto ejecutadas ni compuertas aprobadas.

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
4. Jorge inicia su etapa en `etapa/01-datos-ml`. Los demás esperan la aceptación de la etapa anterior.
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

Las carpetas `apps/web`, `apps/mobile`, `services/api`, `ml`, `data` y `scripts` se crearán durante las etapas correspondientes. No hay comandos de ejecución del producto todavía: documentarlos cuando existan, junto con versiones y lockfiles.

## Seguridad y alcance

No publicar claves ni datos personales. Cifras de mockups son ficticias; datos reales con fuentes y versiones. Separar observado, predicho y simulado. Gemini apagado por defecto, opcional y sin facturación. No predicción individual ni persuasión partidista. Ante un defecto previo, pausar etapa activa, corregir con su autor, revisar y reanudar sin trabajo simultáneo.

## Revisión y protección

Trabajar mediante ramas y PR, sin push directo ni force push a main después de esta inicialización. Configurar protección de main, aprobación humana y verificaciones cuando permisos y plan lo permitan. No se ha activado protección ni CI automáticamente; no hay comprobaciones de producto implementadas.
