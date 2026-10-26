# Acta de relevo G1

Estado: PENDIENTE DE REVISIÓN HUMANA
Responsable: Jorge
Revisora: Lluvia
Rama de trabajo: etapa/01-datos-ml
Destino: develop
PR: PENDIENTE DE CREAR
Commit de implementación: PENDIENTE DE REGISTRAR
SHA de merge: PENDIENTE (no integrado)
Aceptación humana: PENDIENTE (no firmada por IA)

## Entregables verificables

- Fuentes/versiones: data/sources.lock.json; source_version ine-ccpc-jal-b76f8fc46187.
- Dataset y catálogo: data/processed/participation.csv, territories.json, elections.json, metadata.json.
- Diccionario: data/dictionary.csv.
- Modelo/evaluación: ml/artifacts/random_forest.joblib y evaluation.json; snapshot predictions_2024.json; errores por municipio.
- Hashes: data/artifacts.sha256.json. Contrato 1.1.0: contracts/openapi.yaml y CONTRACT_STATUS.json.
- Pruebas: 19 aprobadas; evidencia en docs/evidencias/etapa-1. Métodos y traspaso en docs/METODOLOGIA_G1.md y docs/ENTREGA_LLUVIA_G1.md.

## Criterios G1 (comprobación técnica, pendiente aceptación de Lluvia)

1. Seis elecciones oficiales, claves/nombres continuos de 125 municipios, pipeline ejecutado y trazable: evidencia data_validation.json.
2. CSV municipal sin datos personales; conteos, faltantes y denominadores explícitos; no inventar cifras: data/README.md.
3. Baseline y RF con partición temporal, métricas reales y versión; sin intervalo inventado: evaluation.json.
4. Reconstrucción aislada y dependencias fijadas: clean_environment.json y pruebas de reproducción.
5. Contrato con ejemplos válidos y diferencias registradas antes de implementar consumidores: contracts/CONTRACT_STATUS.json.

## Limitaciones y cambios de alcance para revisar

Cobertura acotada a Jalisco, municipios INE. Son tasas entre registros conocidos de CCPC, no cómputos partidistas. Solo backtest 2024, no pronóstico de años futuros. Geometría no disponible y equivalencia espacial no verificada; endpoint mapa debe responder 503 hasta incorporar correspondencia documentada. Interval=null. La continuidad de claves no prueba estabilidad de límites. Estas limitaciones están documentadas y no deben ocultarse en la demo.

## Reconstruir

Desde clon limpio con Python3.12: instalar requirements.lock y paquete editable (README), python -m civia_data.verify, python -m pytest -q. Reconstrucción de fuentes: python -m civia_data.download; python -m civia_data.build; python -m civia_data.train; python -m civia_data.verify. Detenerse ante error. No hay llaves API ni gasto.

## Relevo

Lluvia revisa y acepta o solicita cambios; después integrar PR aprobado a develop y registrar SHA real de merge mediante PR de documentación si hace falta. Solo entonces se habilita G2. No se ha comenzado su implementación.
