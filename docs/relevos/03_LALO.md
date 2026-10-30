# Acta de relevo
Estado: ACEPTADA POR AUTORIZACION EXPLICITA DE VIVIANA
Etapa y compuerta: 3 / G3
Responsable: LALO
Revisor: Viviana
Fecha, hora, America/Hermosillo: 2026-10-28; hora no registrada
Destino de integración: develop
PR y SHA integrado: PR [#7](https://github.com/GeorgieRe2rn/CIVIA/pull/7); HEAD `89ffdaf`; merge mediante Squash and merge; SHA en `develop`: `fec9404cb642080c571cde9629c365c510f34fcd`
Dataset, modelo, contrato y hashes: fuente `ine-ccpc-jal-b76f8fc46187`; contrato OpenAPI `1.1.0`; predicción y escenario servidos por API G2
Archivos y comandos reproducibles: `apps/web`; `cd apps/web`; `npm install`; `npm run typecheck`; `npm run build`; evidencia en `docs/evidencias/etapa-3/RESULTADOS.md`
Pruebas, resultado y evidencia: typecheck y build correctos; integración real verificada en `http://localhost:5173`; `npm audit --omit=dev` sin vulnerabilidades
Criterios aprobados uno por uno: implementados en código, verificados localmente y comprobados por el check remoto `verify`. GitHub no registra una revisión separada porque la cuenta autenticada era la autora del PR; la autorización humana explícita de Viviana se registra en esta acta. Mapa validado con fallback `503 DATA_UNAVAILABLE` por falta de geometría verificada y con render SVG para GeoJSON válido.
Validación posterior PostgreSQL/PostGIS: 2026-10-30; contenedor temporal `postgis/postgis:16-3.4`; PostgreSQL `16.4`; PostGIS `3.4.3`; migración aplicada; ingesta repetida sin duplicados; 125 territorios, 750 observaciones y 125 predicciones; suite `31 passed`. La corrección de `services/api/app/store.py` evita enviar `geometry` como `VARCHAR` cuando permanece nula.
Limitaciones / bloqueos: no hay geometría local; CORS por defecto usa `http://localhost:5173`; no se ha probado teléfono/LAN; móvil, E2E y CI integral siguen pendientes.
Cambios de alcance autorizados: se implementó con las especificaciones textuales recibidas; no había archivos de mockup en el repositorio.
Firma del responsable:
Aceptación del revisor humano: Viviana; autorización explícita en esta sesión. No existe aprobación GitHub separada porque la cuenta autenticada era la autora del PR.
Siguiente persona habilitada: VIVIANA; PostgreSQL/PostGIS ya fue validado localmente; G4 móvil sigue sin iniciar y requiere sus propias verificaciones.
No aceptar con fallas P0. No inventar evidencia.
