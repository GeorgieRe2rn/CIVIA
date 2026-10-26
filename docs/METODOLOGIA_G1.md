# Método y límites de G1

## Alcance

Jalisco, municipios con claves INE, elecciones federales 2009, 2012, 2015, 2018, 2021 y 2024. En 2012/2018/2024 hay concurrencia presidencial; 2009/2015/2021 son intermedias. El objetivo es la abstención entre registros de condición conocida de los CCPC, no intención individual ni resultado de una candidatura. Ver definición y NS en data/README.md.

## Variables e independencia temporal

Para un objetivo t se usan abstención municipal de t-6, abstención de t-3, log(1+LN de t-3), porcentaje NS de t-3 y tipo de elección t (calendario conocido antes de votar). No se usa LN, SV, NV, NS ni participación de t. Los años 2009/2012 inicializan rezagos y no tienen ejemplos entrenables por falta de t-6. No hay imputación ni mezcla aleatoria entre años.

Baseline = abstención del mismo municipio seis años antes, con el mismo tipo de elección. Se compara en exactamente las mismas 125 filas del modelo. Se evalúa con MAE y RMSE en puntos porcentuales, sin ponderación poblacional: mide error de municipio medio, no error nacional.

## Selección y prueba

RandomForestRegressor fijo: 200 árboles, profundidad máxima 4, hoja mínima 10, random_state=42, n_jobs=1. No se exploran hiperparámetros después de observar 2024.

1. Ajuste inicial en 2015 y 2018 (250 ejemplos); validación 2021 (125). Elegir RF o baseline por menor MAE en 2021.
2. Reajustar el candidato RF en 2015/2018/2021 (375 ejemplos). Medir una sola prueba final en 2024 (125).
3. Publicar ambas métricas 2024 incluso si contradicen la selección. La estrategia elegida por validación no se cambia por mirar el test.

Los municipios aparecen en años de entrenamiento y prueba porque el uso es longitudinal sobre los mismos municipios. Ninguna fila de 2024 entra en entrenamiento ni se separan aleatoriamente filas del mismo año. No se mide generalización a municipios nuevos. La validación 2021 es intermedia y el test 2024 concurrente: ese cambio de contexto es una limitación adicional. Una sola elección final de prueba no demuestra estabilidad futura.

## Incertidumbre y disponibilidad

`interval=null`: no hay una elección adicional independiente para calibrar intervalos. La dispersión de árboles no se presenta como intervalo fiable. Mostrar "Intervalo no disponible".

El artefacto de inferencia listo para API es `ml/artifacts/predictions_2024.json`, un backtest identificado como `retrospective_holdout`. NO es un pronóstico para 2030 ni una predicción entrenada con resultados 2024. Requests a otros objetivos se rechazan con 422 hasta contar con un nuevo artefacto y validación. El modelo joblib se conserva para reproducción; cargar únicamente el artefacto propio verificado y con las versiones fijadas, nunca archivos de terceros.

El producto debe mostrar "estimación retrospectiva evaluada para 2024" junto con observado/predicho/simulado, MAE, baseline, muestra, fuentes, sistema de claves, denominador y advertencias. No afirmar causalidad, efectos de transporte o persuasión de votantes.

## Referencias técnicas

- INE, portal CCPC: https://portal.ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/
- scikit-learn, RandomForestRegressor: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
- scikit-learn, evaluación: https://scikit-learn.org/stable/modules/cross_validation.html

## Estado de etapas

G1 implementa únicamente datos, ML y contrato. No se implementó FastAPI/PostgreSQL, web, app móvil ni mapa. Lluvia revisa G1 y, tras aceptación humana e integración a develop, comienza G2. Si exige cambios del contrato 1.1.0, resolverlos dentro de G1 antes de aceptarlo.
