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
Commit G4 publicado y verificado: `604ce83`, rama publicada en `origin`; PR G4 #10 abierto hacia
`develop`. No se hizo push directo a `develop`.

Cambios actuales: cliente Expo/React Native en `apps/mobile`, cliente tipado
contra la API G2, estados de carga/error/vacio/sin conexion, fallback de mapa y
configuracion de API para emulador, simulador y LAN.

Pruebas actuales: móvil con `npm ci`, `npm run typecheck`,
`npx expo export --platform android`, `npx expo-doctor` (`20/20`) y
`npm audit --omit=dev --audit-level=high`; web con typecheck, build y E2E
`3/3`; API con `31 passed`; PostgreSQL/PostGIS fresco con migración, doble
ingesta y endpoints verificados. Prueba viva móvil: AVD
`Pixel_9_Pro_API_35`, dispositivo `emulator-5554`, Expo con
`EXPO_PUBLIC_API_BASE_URL=http://10.0.2.2:8000`, API `200`, conexión TCP y
datos cargados en la pantalla (125 territorios).
Evidencia: `docs/evidencias/etapa-4/RESULTADOS.md`.

Limitaciones: se probó emulador Android, pero no teléfono físico/LAN; geometria territorial
sigue ausente; quedan 7 vulnerabilidades bajas transitivas de Expo CLI; no hay
aprobacion humana de Jorge registrada; el PR #10 aún no está integrado.

Siguiente paso: solicitar la revision autentica de Jorge, probar teléfono
físico/LAN y, si procede, integrar el PR #10 hacia `develop`; después actualizar
esta acta solo con resultados reales.
