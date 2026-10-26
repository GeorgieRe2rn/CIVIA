# GitHub paso a paso: ramas, push, PR y merge

## Diccionario sin tecnicismos

- Repositorio: carpeta compartida del proyecto, con historial en GitHub.
- Rama: línea de trabajo separada; permite cambiar archivos sin alterar otras versiones.
- Commit: punto guardado en el historial local, con descripción de los cambios.
- Push: subir commits a la misma rama en GitHub; no los integra a otra rama.
- Pull: traer cambios de GitHub al clon local; no confundir con Pull Request.
- PR (Pull Request): solicitud para revisar e integrar cambios de una rama a otra.
- Revisión/aprobación: otra persona comprueba código, pruebas y evidencia. No equivale a integrar.
- Merge: integrar los cambios de un PR aprobado en su rama de destino.
- Conflicto: Git no puede combinar cambios automáticamente; resolver revisando ambos contenidos y probando, sin sobrescribir a ciegas.

## Las tres clases de rama

1. Rama de etapa: aquí trabaja y hace pushes cada integrante.
2. develop: reúne etapas revisadas y probadas. Se actualiza mediante PR.
3. main: conserva la versión estable aprobada para entrega. Recibe un PR final desde develop.

Flujo obligatorio: develop -> rama de etapa -> push a esa rama -> PR hacia develop -> revisión y pruebas -> merge -> relevo aceptado -> siguiente etapa.
Al terminar: develop -> pruebas integrales -> PR hacia main -> revisión final -> merge -> verificar main y etiquetar release.

No hacer push directo ni force push a develop o main después de la creación inicial de develop. Revisar una etapa no autoriza implementar la siguiente en paralelo. main contiene inicialmente solo coordinación; eso no significa que la aplicación esté terminada.

## Quién hace cada PR

| Responsable | Rama de trabajo | Destino del PR | Revisor |
| --- | --- | --- | --- |
| Jorge | etapa/01-datos-ml | develop | Lluvia |
| Lluvia | etapa/02-api | develop | Lalo |
| Lalo | etapa/03-web | develop | Viviana |
| Viviana | etapa/04-mobile-release | develop | Jorge |
| Viviana prepara la entrega | develop | main | Jorge y confirmación del equipo |

## Inicio: primera vez

Clonar solo si todavía no tienes el repositorio:

```sh
git clone https://github.com/GeorgieRe2rn/CIVIA.git
cd CIVIA
git fetch origin
git switch --track origin/develop
```

Si develop ya existe localmente, usar `git switch develop` en lugar del último comando. Si ya tienes un clon, comenzar con `git status` y resguardar cambios antes de cambiar ramas; no borrar ni descartar trabajo.

## Empezar tu etapa

Confirmar acta anterior ACEPTADA y PR integrado en develop; Jorge inicia sin acta anterior.

```sh
git switch develop
git pull --ff-only
```

Después ejecutar SOLO el comando de tu persona:

- Jorge: `git switch -c etapa/01-datos-ml`
- Lluvia: `git switch -c etapa/02-api`
- Lalo: `git switch -c etapa/03-web`
- Viviana: `git switch -c etapa/04-mobile-release`

Si tu rama ya existe, usar git switch con su nombre y revisar su historial; no recrearla ni forzarla. Si pull falla por divergencias, detenerse y pedir revisión antes de resetear.

## Guardar y subir avances

Ejemplo para Jorge; los otros sustituyen SOLO el nombre de rama por el suyo:

```sh
git status
git diff
```

Agregar rutas concretas de los archivos revisados con git add. Ejecutar pruebas relevantes y después:

```sh
git diff --cached
git commit -m "Describir el cambio realizado"
git push -u origin etapa/01-datos-ml
```

Nunca subir .env real, contraseñas o claves. Un push deja cambios en la rama de trabajo, NO en develop ni main. Puede abrirse un PR borrador para comentar avances, pero no integrar ni empezar la siguiente etapa antes de cumplir criterios.

## Abrir el PR en la página de GitHub

1. Abrir el repositorio > Pull requests > New pull request.
2. En base elegir develop (destino). En compare elegir TU rama de etapa (origen). Verificar que NO diga main como base.
3. Revisar los archivos y pulsar Create pull request. Completar plantilla con etapa, cambios, instalación, comandos realmente ejecutados, resultados, evidencia y limitaciones.
4. Asignar al revisor según tabla. Si no aparece o no tienes permisos, Jorge confirma acceso; no asumir aprobación.
5. Revisor deja comentarios o aprueba. Autor corrige en la misma rama y vuelve a hacer push: el PR se actualiza solo.
6. Con revisión humana aprobada y pruebas pertinentes correctas, integrar con Squash and merge. No confundir una aprobación con un merge ya realizado.
7. Registrar el enlace al PR integrado y SHA final verificable. Completar acta y obtener aceptación humana. Si el SHA se conoce después del merge, registrarlo en un pequeño PR posterior hacia develop antes de iniciar la siguiente etapa.

## Relevo y bloqueos

Solo con PR integrado en develop, evidencia y acta ACEPTADA comienza la siguiente persona desde develop actualizado. No inventar firmas ni pruebas. Un defecto previo pausa la etapa activa; su autor corrige mediante rama desde develop y PR hacia develop, después se valida y reanuda. Una persona desarrolla a la vez.

## Entrega final: develop hacia main

1. Viviana verifica sobre el commit candidato de develop: instalación limpia, API, datos, ML, web, Expo físico, coherencia entre clientes, errores/red, fuentes, seguridad y documentación. Registrar resultados reales y hashes. No basta con que una pantalla abra.
2. Si falla algo, corregir por rama y PR hacia develop; volver a verificar lo afectado. No promover a main con bloqueos P0.
3. Abrir PR con base main y compare develop. Título: Release CIVIA v1.0.0. Adjuntar evidencia y estado de las cuatro compuertas.
4. Jorge revisa y el equipo confirma entrega. Si develop cambia después de probar, verificar el nuevo candidato antes de integrar.
5. Usar Create a merge commit en este PR final para conservar la relación entre develop y main. Si esa opción no está disponible, coordinar la estrategia y documentarla antes de integrar.
6. Verificar main después del merge; si falla, no etiquetar ni entregar. Crear la etiqueta v1.0.0 sobre el commit estable verificado en main, publicar release y respaldar. Confirmar hora/medio de entrega oficiales.

## Configuración pendiente del propietario

Jorge invita colaboradores y confirma cuentas. Configurar protección de develop y main con PR y aprobación humana cuando plan/permisos lo permitan. La rama por defecto de GitHub puede seguir siendo main: por eso siempre seleccionar base develop manualmente para los PR de etapa. No se ha activado protección ni CI; las verificaciones de producto se añaden durante implementación, sin simular checks aprobados.
