# Acta de relevo

Estado: EN DESARROLLO; NO ACEPTADA
Etapa y compuerta: 4 / G4
Responsable: Viviana
Revisor: Jorge
Fecha, hora, America/Hermosillo: 2026-10-30; hora no registrada
Destino de integración: develop
Rama de trabajo: `etapa/04-mobile-release`
Dependencia: G3 integrada mediante PR #7 y PR #8; acta G3 aceptada por
autorizacion explicita. La correccion PostGIS sigue en el PR #9 abierto.
Commit de trabajo: `50ff308`, rama publicada en `origin`; PR G4 hacia
`develop` aun no creado porque los POST autenticados al API de GitHub agotaron
timeout. No se hizo push directo a `develop`.

Cambios actuales: cliente Expo/React Native en `apps/mobile`, cliente tipado
contra la API G2, estados de carga/error/vacio/sin conexion, fallback de mapa y
configuracion de API para emulador, simulador y LAN.

Pruebas actuales: móvil con `npm ci`, `npm run typecheck`,
`npx expo export --platform android`, `npx expo-doctor` (`20/20`) y
`npm audit --omit=dev --audit-level=high`; web con typecheck, build y E2E
`3/3`; API con `31 passed`; PostgreSQL/PostGIS fresco con migración, doble
ingesta y endpoints verificados.
Evidencia: `docs/evidencias/etapa-4/RESULTADOS.md`.

Limitaciones: no se ha probado telefono fisico/LAN; geometria territorial
sigue ausente; quedan 7 vulnerabilidades bajas transitivas de Expo CLI; no hay
aprobacion humana de Jorge registrada; falta crear el PR G4.

Siguiente paso: crear el PR G4, ejecutar CI remoto, probar en dispositivo/LAN,
solicitar la revision autentica de Jorge y actualizar esta acta solo con
resultados reales.
