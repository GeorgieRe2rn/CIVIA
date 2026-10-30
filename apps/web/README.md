# CIVIA Web

Etapa G3 de Lalo: cliente React/TypeScript/Vite para explorar la participacion
agregada de CIVIA. La aplicacion consulta la API G2 real; no contiene cifras de
demo ni datos simulados en el cliente.

## Requisitos

- Node.js 22 o compatible con Vite 7.
- API G2 disponible en `http://localhost:8000`.
- Abrir el frontend en `http://localhost:5173` para coincidir con el CORS local
  de la API.

## Desarrollo

```powershell
npm install
$env:VITE_API_BASE_URL="http://localhost:8000"
npm run dev
```

Comandos de validacion:

```powershell
npm run typecheck
npm run build
npm audit --omit=dev
```

## Alcance

- `Inicio`: resumen de observado, predicho y simulado.
- `Datos`: comparador y tabla completa de observaciones.
- `Mapa`: render SVG proporcional de GeoJSON verificado si la API lo entrega; de
  lo contrario muestra una alternativa textual y no dibuja cartografia inventada.
- `Prediccion`: backtest retrospectivo `federal-2024`, con MAE, advertencias y
  trazabilidad.
- `Escenarios`: delta hipotetico entre `-20` y `+20` pp calculado por backend.
- `Ayuda`: explicaciones deterministas; el asistente opcional solo aparece si
  `/api/health` informa `ai_enabled=true`.

La base, los estados de carga/error/vacio, el denominador `SV+NV`, las fuentes
y la version de datos se muestran junto con los resultados para conservar la
trazabilidad.
