# Instrucciones para los cuatro

Estos archivos ya están incorporados. Nadie necesita subir otra copia del kit.

## Iniciar una etapa

Confirmar que el acta anterior está ACEPTADA y su PR integrado. Jorge inicia sin acta previa. Desde el clon, ejecutar:

```sh
git switch main
git pull --ff-only
```

Después crear SOLO la rama que corresponda:

- Jorge: `git switch -c etapa/01-datos-ml`
- Lluvia: `git switch -c etapa/02-api`
- Lalo: `git switch -c etapa/03-web`
- Viviana: `git switch -c etapa/04-mobile-release`

Si la rama ya existe, usar `git switch nombre-de-rama` y revisar su estado, sin borrarla ni forzarla.

## Durante el trabajo

Crear tarea en Issues con responsable, dependencia, alcance, aceptación, fecha y evidencia. Modificar solo lo necesario; revisar git diff antes de cada commit. Agregar archivos concretos, evitando secretos, y hacer commit con explicación clara. Publicar la rama usando `git push -u origin nombre-de-rama` (sustituir por la rama real).

## Terminar y entregar

1. Ejecutar las pruebas pertinentes reales e instalación limpia. Guardar evidencia sanitizada en docs/evidencias/etapa-N.
2. Completar el acta propia en docs/relevos con rutas, resultados, limitaciones y referencia al PR. Estado PENDIENTE hasta revisión.
3. Abrir Pull Request en GitHub contra main y seleccionar al revisor indicado en README. La plantilla aparece automáticamente.
4. Revisor humano verifica y acepta o registra BLOQUEADO. No inventar firmas, resultados ni SHA.
5. Integrar PR aprobado. Registrar el SHA integrado en el acta mediante actualización posterior revisada si aún no estaba disponible al redactarla. El siguiente no comienza sin aceptación y referencia al merge verificable.

Si falta un criterio P0, no avanzar. No eliminar fallas del acta para aparentar cierre. Si surge un defecto de una etapa previa, pausar desarrollo, corregir con el autor y revisar antes de reanudar.

## Qué consultar

La guía personal contiene calendario, tareas y reglas completas. contracts/openapi.yaml define comunicación. docs/relevos contiene estado de entregas. Una IA ayuda a editar y probar, pero no aprueba compuertas humanas.
