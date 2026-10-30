# Evidencia tecnica G3

Estado de acta: PENDIENTE. Esta evidencia no sustituye la revision humana, la
PR ni la integracion en `develop`.

## Entorno

- Rama: `etapa/03-web`.
- Node.js: `22.13.0`.
- npm: `10.9.2`.
- API local: Uvicorn en `http://localhost:8000`.
- Frontend local: Vite en `http://localhost:5173`.
- Version de datos observada: `ine-ccpc-jal-b76f8fc46187`.
- Contrato consumido: OpenAPI `1.1.0`.

## Comandos ejecutados

```powershell
cd apps/web
npm install
npm run typecheck
npm run build
npm audit --omit=dev
```

Resultados observados:

- Instalacion correcta; lockfile generado en `apps/web/package-lock.json`.
- `npm run typecheck`: codigo de salida 0.
- `npm run build`: codigo de salida 0; Vite `7.3.7`, 30 modulos transformados.
- `npm audit --omit=dev`: `found 0 vulnerabilities`.

## Integracion real

Con la API G2 levantada se verifico en navegador:

- `/api/health`: `200`, `status=ok`, `ai_enabled=false`.
- `/api/territorios`: `200`, catalogo de 125 municipios.
- `/api/elecciones`: `200`, seis elecciones de 2009 a 2024.
- `/api/participacion?territorio=14001`: `200`, seis observaciones.
- `/api/predicciones`: `200`, prediccion 2024 de `52.0%` para Acatic.
- `/api/mapa?territorio=14001`: `503 DATA_UNAVAILABLE`; la interfaz muestra la
  alternativa textual y no dibuja cartografia inventada.
- La rama de GeoJSON válido también se verificó con una respuesta con forma del
  contrato: renderiza un SVG accesible con un path proporcional y conserva la
  lista textual.
- `/api/escenarios` con `delta_pp=3`: `200`, resultado final `55.0%`.
- La vista Ayuda oculta el asistente opcional cuando `ai_enabled=false` y
  conserva la ayuda determinista.

## Responsive y accesibilidad

- Navegacion por botones entre Inicio, Datos, Mapa, Prediccion, Escenarios y
  Ayuda verificada en navegador.
- La capa visual fue refinada con una direccion editorial consistente: bosque
  profundo, papel marfil, acentos coral/teal, titulares serif y estados de
  datos diferenciados.
- Viewport de `360x800`: `documentWidth=345`, `bodyWidth=345`, sin overflow
  horizontal.
- Tabulacion verificada; el foco entra en controles nativos de seleccion.
- Cada vista conserva un `h1` accesible y la vista de datos muestra las seis
  fuentes devueltas por la API.
- Se implementaron estados visibles de carga, error, vacio y no disponible,
  etiquetas de formulario, tabla con encabezados y foco `:focus-visible`.

## Limitaciones

- El entorno local de G2 no tiene geometria verificada, por eso el mapa solo se
  pudo validar mediante su fallback `503`.
- El navegador registra el `503` del mapa como recurso fallido, aunque el
  cliente lo captura y presenta el estado accesible esperado.
- El CORS local de la API acepta por defecto `http://localhost:5173`; para usar
  `127.0.0.1:5173` se debe configurar `CORS_ORIGINS` explicitamente.
- No se ejecutaron pruebas desde telefono/LAN, PR, push, merge ni aceptacion
  humana.
