# Entrega técnica para revisión de Lluvia

Estado: PENDIENTE DE REVISIÓN HUMANA. No comenzar G2 antes de aprobación, integración del PR en develop y acta aceptada.

## Qué recibes

- CSV de 750 registros, catálogo municipal INE, elecciones y metadatos: data/processed.
- Orígenes/versiones/hash: data/sources.lock.json; diccionario: data/dictionary.csv.
- Modelo reproducible, evaluación, error por municipio y predicciones 2024: ml/artifacts.
- Contrato OpenAPI 3.0.3, versión de API 1.1.0 y ocho ejemplos rastreables: contracts.
- Pruebas y evidencia local: tests y docs/evidencias/etapa-1.

## Contrato propuesto para congelar en G1

Los siete endpoints iniciales se mantienen y se añade GET /api/elecciones para no hardcodear el catálogo en los clientes. Se agregan campos de conteos/NS, denominador, fechas, sistema INE y modo retrospectivo; ningún cliente está implementado todavía. Ver CONTRACT_STATUS.json para versión y hashes. El hash congela esta propuesta técnica; la aceptación final sigue pendiente de tu revisión.

GET /api/territorios filtra estado 14 opcional; catálogo válido pero sin resultados: []. GET /api/participacion requiere territorio, filtra elección opcional, orden cronológico; municipio inexistente:404, consulta válida sin año:200 con lista vacía. Predicciones/escenarios solo aceptan federal-2024: otros objetivos422; artefacto faltante503. Las respuestas incluyen meta con source_version, timestamp UTC de servicio y warnings, data y fuentes. Los ejemplos usan timestamp fijo de adquisición para ser reproducibles; el servidor debe generar el suyo al responder.

GET /api/mapa: **503 DATA_UNAVAILABLE en G1**, porque no se incluyen geometrías verificadas. No producir un mapa falso. Resolver correspondencia INE/INEGI al incorporar cartografía. El contrato GeoJSON usa properties.territory_id en el sistema INE.

## Lo que debes preservar al implementar

1. Guadalajara = 14041 en estos datos, no la clave INEGI 14039. Pasar la misma ID a ambos clientes. No unir cartografía por nombre.
2. Fuente son los CCPC: tasas SV/(SV+NV), NS separado. No decir que son cómputos de partidos ni participación total sin advertencia.
3. No entrenar en cada petición. Consumir snapshot verificado predictions_2024.json con métricas reales, interval=null, warnings y evaluation_mode. La carga de joblib no es necesaria para servir ese backtest.
4. Escenario parte de participación predicha, aplica delta_pp y clamp 0-100; devolver abstención complementaria y clamped. No partir del dato observado cuando el contrato pide base predicha.
5. PostgreSQL debe guardar IDs de texto, elección/tipo, conteos, versión/fuentes y restricciones. Ingestión idempotente por territory_id+election_id. No redondear porcentajes durante el almacenamiento y cálculo.
6. La explicación determinista funciona sin claves ni gasto. IA apagada por defecto. Las llaves y datos sensibles nunca van en clientes.

Ver README para reconstrucción desde clon limpio y docs/COMO_TRABAJAMOS para PR/relevo.
