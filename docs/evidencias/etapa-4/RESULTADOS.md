# Evidencia tecnica G4

Estado: EN DESARROLLO. Esta evidencia no sustituye la revision de Jorge ni la
aceptacion del acta.

## Alcance implementado

- Cliente Expo/React Native en `apps/mobile` con Expo `58.0.21`, React `19.3.0`
  y React Native `0.88.1`.
- Cliente tipado contra los mismos endpoints OpenAPI de G2: health, catalogos,
  participacion, prediccion, escenarios, mapa y asistente.
- URL configurable con `EXPO_PUBLIC_API_BASE_URL`; el README documenta valores
  de Android emulator, simulador iOS y telefono en LAN.
- Estados visibles de carga, error, vacio y sin conexion.
- Mapa solicitado solo al abrir la pestaña y fallback `503 DATA_UNAVAILABLE`
  cuando la API no entrega geometria verificada.

## Comandos ejecutados

Desde `apps/mobile`:

```powershell
npm ci
npm run typecheck
npx expo export --platform android
npx expo-doctor
npm audit --omit=dev --audit-level=high
```

Resultados observados:

- `npm run typecheck`: codigo de salida 0.
- `npx expo export --platform android`: bundle Android generado correctamente.
- `npx expo-doctor`: `20/20` comprobaciones correctas.
- La auditoria no reporta vulnerabilidades altas; quedan 7 bajas en
  `deepmerge`, dependencia transitiva de Expo CLI. No se aplico el downgrade
  forzado que propone npm hacia Expo 51.

Desde `apps/web`:

```powershell
npm ci
npm run typecheck
npm run build
npm run e2e
```

Resultados observados:

- `npm run typecheck`: codigo de salida 0.
- `npm run build`: build Vite generado correctamente.
- `npm run e2e`: `3 passed`; cubre catalogos/historico, escenario y fallback
  de mapa sin geometria.

El workflow `.github/workflows/integral.yml` reproduce API, PostGIS, web,
móvil y E2E en Actions. La ejecución push del commit G4 `604ce83` terminó
`success`: `API y contrato`, `PostgreSQL y PostGIS`, `Web y compilacion`,
`Mobile Expo` y `E2E web contra API` pasaron. Evidencia:
`https://github.com/GeorgieRe2rn/CIVIA/actions/runs/41144688515`.

La rama `etapa/04-mobile-release` está publicada en `origin` con el commit G4
`604ce83`. El PR G4 #10 hacia `develop` está abierto y sus checks de integración
pasaron en `https://github.com/GeorgieRe2rn/CIVIA/actions/runs/41174335091`.
El check histórico de G1 también pasó en
`https://github.com/GeorgieRe2rn/CIVIA/actions/runs/41174335333`. No se hizo
push directo a `develop`; el PR es
`https://github.com/GeorgieRe2rn/CIVIA/pull/10`.

## Prueba viva del emulador Android

- AVD: `Pixel_9_Pro_API_35`; dispositivo ADB: `emulator-5554`.
- Expo: `EXPO_PUBLIC_API_BASE_URL=http://10.0.2.2:8000`.
- API host: `200`; conexión TCP Android hacia `10.0.2.2:8000`: correcta.
- La pantalla móvil mostró estado `API`, etiqueta `CIVIA`, 125 territorios,
  seis elecciones y valores observados/predichos.
- Esto valida el emulador; no sustituye una prueba en teléfono físico por LAN.

## Validacion PostgreSQL local

En un contenedor fresco `postgis/postgis:16-3.4` se ejecutaron migracion,
ingesta dos veces y `python scripts/verify_postgres.py`:

- PostGIS `3.4.3`; 6 fuentes, 125 territorios, 6 elecciones, 750
  participaciones, 1 modelo y 125 predicciones.
- Duplicados de participacion y predicciones: 0; geometria no nula: 0.
- Health, catalogos, historial, prediccion, escenario, asistente y OpenAPI
  correctos; mapa `503 DATA_UNAVAILABLE` de forma consistente.

## Pendientes verificables

- Ejecutar la aplicacion en un telefono fisico conectado por LAN con la API
  escuchando en una interfaz accesible.
- Revisar y, si procede, integrar el PR G4 #10 hacia `develop`.
- Revisar y aceptar el relevo mediante la cuenta autentica de Jorge.
- No hacer push directo a `develop`.
