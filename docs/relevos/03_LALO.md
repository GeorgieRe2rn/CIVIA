# Acta de relevo
Estado: PENDIENTE
Etapa y compuerta: 3 / G3
Responsable: LALO
Revisor: Viviana
Fecha, hora, America/Hermosillo: 2026-10-28; hora no registrada
Destino de integración: develop
PR y SHA integrado: PENDIENTE; no se ha creado PR ni commit G3
Dataset, modelo, contrato y hashes: fuente `ine-ccpc-jal-b76f8fc46187`; contrato OpenAPI `1.1.0`; predicción y escenario servidos por API G2
Archivos y comandos reproducibles: `apps/web`; `cd apps/web`; `npm install`; `npm run typecheck`; `npm run build`; evidencia en `docs/evidencias/etapa-3/RESULTADOS.md`
Pruebas, resultado y evidencia: typecheck y build correctos; integración real verificada en `http://localhost:5173`; `npm audit --omit=dev` sin vulnerabilidades
Criterios aprobados uno por uno: implementados en código y verificados localmente; revisión humana PENDIENTE. Mapa validado con fallback `503 DATA_UNAVAILABLE` por falta de geometría verificada y con render SVG para GeoJSON válido.
Limitaciones / bloqueos: no hay geometría local; CORS por defecto usa `http://localhost:5173`; no se ha probado teléfono/LAN; no hay PR, push ni merge.
Cambios de alcance autorizados: se implementó con las especificaciones textuales recibidas; no había archivos de mockup en el repositorio.
Firma del responsable:
Aceptación del revisor humano:
Siguiente persona habilitada: VIVIANA, sujeto a aceptación de esta acta
No aceptar con fallas P0. No inventar evidencia.
