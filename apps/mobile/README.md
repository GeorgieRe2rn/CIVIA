# CIVIA Mobile

Cliente G4 de CIVIA con Expo/React Native. Consume la misma API G2 que la web;
no duplica datos ni calcula cifras en el dispositivo.

## Instalacion

Requiere Node.js 22.13+ y Expo Go en un telefono. Desde `apps/mobile`:

```powershell
npm ci
npm run typecheck
npm start
```

Para un telefono en la misma red, define la URL de la computadora antes de
arrancar Expo. La API debe aceptar el origen del dispositivo mediante
`CORS_ORIGINS`:

```powershell
$env:EXPO_PUBLIC_API_BASE_URL="http://192.168.1.10:8000"
npm start
```

El valor por defecto es `http://10.0.2.2:8000` en Android y
`http://localhost:8000` en iOS/simulador. El asistente muestra la URL activa
para que un fallo de LAN no se confunda con datos vacios.

## Flujos

- Inicio: estado de API, territorio seleccionado y resumen observado/predicho.
- Datos: seis observaciones historicas del territorio y su fuente.
- Mapa: solicita `/api/mapa` solo al abrir la vista; conserva el fallback
  `503 DATA_UNAVAILABLE` sin dibujar geometria inventada.
- Prediccion: backtest `federal-2024`, con advertencias y trazabilidad.
- Escenarios: simulaciones `-5`, `0` y `+5` puntos porcentuales.
- Ayuda: consulta determinista y explicacion de fuentes, limites y conexion.

Cada flujo tiene estados de carga, error, vacio y sin conexion. La prueba en
telefono/LAN debe ejecutarse con la API levantada en una interfaz accesible;
el CI comprueba tipos y el cliente, pero no suplanta un dispositivo fisico.

Leer `contracts/openapi.yaml` y `docs/ENTREGA_LLUVIA_G1.md` antes de cambiar
el contrato.
