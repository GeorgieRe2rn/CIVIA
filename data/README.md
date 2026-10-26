# Datos oficiales y derivados G1

`sources.lock.json` fija las seis descargas INE, URLs, fecha de adquisición UTC, miembro Jalisco y SHA256 tanto del ZIP como del CSV. `raw/` es caché local ignorada: reconstruir con `python -m civia_data.download`. El descargador rechaza cambios de versión en lugar de aceptarlos silenciosamente.

`processed/participation.csv`: 125 municipios × seis elecciones = 750 filas, sin datos individuales. `territories.json`, `elections.json` y `metadata.json` acompañan la tabla. `dictionary.csv` define campos y unidades. `artifacts.sha256.json` verifica datos, modelo y contrato; no incluye su propio hash.

## Definiciones que deben aparecer en el producto

- LN: registros de los cuadernillos incluidos. SV: con marca de voto. NV: sin marca. NS: condición no especificada. Se exige LN=SV+NV+NS.
- Participación conocida: `100*SV/(SV+NV)`. Abstención conocida: `100*NV/(SV+NV)` = 100-participación conocida. Son tasas entre registros de condición conocida, NO SV/LN ni una tasa completa del padrón.
- NS se conserva como conteo y porcentaje de LN; NO se suma a NV.
- Extremos por faltantes: `100*SV/LN` y `100*(SV+NS)/LN`. Son límites aritméticos, no intervalos de confianza ni del modelo.
- Excluye casillas especiales y voto exterior según descripción de INE. El conteo censal no equivale a los cómputos de votos de partidos.
- No promediar porcentajes al agrupar municipios: sumar SV/NV/NS/LN primero. No usar cifras ilustrativas de mockups.

## Claves, territorio y tiempo

El identificador concatena **EDOCVE INE de 2 dígitos + MPIOCVE INE de 3 dígitos**. Guadalajara es **14041**, Puerto Vallarta **14069** en estos archivos. No convertir estas claves en códigos INEGI por similitud ni por nombre. Para cartografía se necesita una correspondencia documentada; G1 no la incluye.

Se verificó igualdad exacta del conjunto de 125 claves y nombres municipales en seis archivos. Esto comprueba continuidad de etiquetas, NO igualdad de polígonos. Las descripciones de los archivos 2009-2021 referencian distritos 2021 y la de 2024 distritos 2023. No unir secciones/distritos entre años; los datos son reconstrucciones retrospectivas y no garantizan disponibilidad histórica en tiempo real.

El CSV 2024 expresa FELECCION como `06/02/2024` aunque el evento fue el 2 de junio. El pipeline reconoce ese formato específico y guarda `2024-06-02`, sin inferencia ambigua de día/mes. Las fechas de las otras jornadas también se fijan explícitamente.

Los registros originales con edad agregada mayor de 120 se conservan y se reportan en validación; no se eliminan ciudadanos por plausibilidad de edad ni se usa edad como variable del modelo. Todos los conteos permanecen trazables.

## Fuentes y condiciones

Portal oficial: https://portal.ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/

ZIP 2009-2021: `https://portal.ine.mx/wp-content/uploads/2022/04/DatosAbiertos_DECEyEC_ConteosCensalesAAAA.zip`; 2024: `https://portal.ine.mx/wp-content/uploads/2025/08/DatosAbiertos_DECEyEC_ConteosCensales2024.zip`. Consultar URLs exactas y hashes en el lock.

Son descargas públicas de datos abiertos del INE; el ZIP no identifica una licencia específica. Atribuir a INE, conservar procedencia y verificar condiciones para redistribución. No afirmar que los datos de terceros tienen una licencia propia del proyecto. Los archivos granulares originales no se publican en este repositorio; se incluyen únicamente agregados municipales derivados.
