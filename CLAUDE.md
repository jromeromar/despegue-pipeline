# Pipeline de diagnóstico comercial Ropofy

Esta carpeta convierte transcripciones de sesiones estratégicas en propuestas
(`propuesta.json`) mediante tres skills encadenadas con compuertas de validación.
El renderizador del lienzo es otra aplicación y consume el `propuesta.json`
que aquí se produce.

---

## Cómo se usa (el consultor)

1. Crear `clientes/<cliente>/entrada/` y soltar ahí la(s) transcripción(es),
   con fecha en el nombre: `2026-08-14-sesion-1.docx`.
2. Decir: **"corre el diagnóstico de <cliente>"**.
3. Recoger los tres JSON en `clientes/<cliente>/salida/` y la agenda de la
   segunda llamada que se entrega al final.

`<cliente>` es un nombre corto sin espacios ni tildes: `activos`, `ayc`.

---

## Cuando el usuario pida "corre el diagnóstico de <cliente>"

Ejecuta las tres etapas **en orden y sin pedir confirmación entre ellas**,
corriendo el validador de cada una antes de pasar a la siguiente y
deteniéndote si alguno falla.

**La regla tiene una sola excepción, y es a propósito: la compuerta de
confirmación de nombres propios** al cierre de la etapa 1. La regla existe para
que el pipeline no pida permiso por cosas que ya están decididas; la grafía de un
nombre propio no está decidida —la transcripción de Teams la destroza— y no hay
forma de deducirla: hay que preguntarla. Es la única parada interactiva de la
cadena. No se agregan otras.

**En corrida desatendida** (tarea programada, cron, sin humano al otro lado) la
compuerta **no bloquea**: las tres etapas corren completas, todos los nombres
quedan `por_confirmar`, y la entrega lo dice **en su primera línea** — «N nombres
propios sin confirmar: la propuesta no se presenta hasta revisarlos». Una corrida
desatendida produce un expediente utilizable, no presentable.

**Etapa 1 — `extraccion-diagnostico`.** Lee su SKILL.md y su contrato de ficha
completos. Produce `clientes/<cliente>/salida/ficha-<cliente>.json` desde las
transcripciones de `clientes/<cliente>/entrada/` (si hay varias, se consolidan
en una sola ficha). Convierte los .docx a texto plano primero. Valida:

    python3 .claude/skills/extraccion-diagnostico/scripts/validar_ficha.py \
      clientes/<cliente>/salida/ficha-<cliente>.json /tmp/trans-<cliente>.txt

Después haz la auto-revisión J1-J6 de
`.claude/skills/extraccion-diagnostico/references/criterios-evaluacion.md`:
una línea por criterio, pasa o duda concreta.

Y **antes de pasar a la etapa 2, corre la compuerta de nombres** (SKILL.md de la
etapa 1, §Compuerta): una tabla con todos los nombres propios —razón social,
marca, cada persona, cada sistema— con su grafía, su estado y las variantes
literales de la transcripción, y una sola pregunta al consultor. Lo que confirme
pasa a `confirmada` con su fuente escrita; lo que corrija se reescribe
conservando las variantes; lo que no sepa queda `por_confirmar`. Después
revalida la ficha y sigue. Corrección aquí = corrección en los tres archivos;
corrección después = rehacer los tres.

**Etapa 2 — `evaluacion-modular`.** Revalida la ficha (compuerta de entrada),
lee su SKILL.md y el catálogo de fugas COMPLETO. Produce
`diagnostico-<cliente>.json`. La nota la escribe el script, nunca el modelo:

    python3 .claude/skills/evaluacion-modular/scripts/calcular_nota.py \
      clientes/<cliente>/salida/diagnostico-<cliente>.json
    python3 .claude/skills/evaluacion-modular/scripts/validar_diagnostico.py \
      clientes/<cliente>/salida/diagnostico-<cliente>.json \
      .claude/skills/evaluacion-modular/references/catalogo-fugas.md \
      clientes/<cliente>/salida/ficha-<cliente>.json

**Etapa 3 — `seleccion-propuesta`.** Revalida ficha y diagnóstico, usa
`libreria/componentes.json`, y produce `propuesta-<cliente>-v1.json`. Copia la
política comercial desde `politica-comercial.json`. Instancias, multiplicador y
precios los escribe el script:

    python3 .claude/skills/seleccion-propuesta/scripts/calcular_condicion.py \
      clientes/<cliente>/salida/propuesta-<cliente>-v1.json \
      clientes/<cliente>/salida/ficha-<cliente>.json
    python3 .claude/skills/seleccion-propuesta/scripts/validar_propuesta.py \
      clientes/<cliente>/salida/propuesta-<cliente>-v1.json \
      libreria/componentes.json \
      clientes/<cliente>/salida/diagnostico-<cliente>.json

**Entrega final, siempre en este formato:**

1. Tabla de los tres archivos con su ruta y su línea de validación.
2. **Estado de los nombres propios**: cuántos quedaron `confirmada` y cuántos
   `por_confirmar`, y la lista de los pendientes con sus variantes. Si hay alguno
   pendiente, esto va **primero**, antes de la tabla: la grafía se imprime en el
   lienzo que el cliente lee, y una propuesta con el apellido del dueño mal
   escrito no se presenta.
3. **Agenda de la segunda llamada**: los `no_capturado` de la ficha
   priorizados — primero los que cambian plan o precio. Las grafías sin confirmar
   van arriba: se resuelven con una foto de una factura o una firma de correo.
4. **Decisiones que requieren criterio humano**: plan recomendado con su razón,
   ajustes manuales de instancias, advertencias que quedaron en pie.

---

## Reglas de la casa (aplican a cualquier tarea en esta carpeta)

1. **El modelo decide QUÉ, Python decide CUÁNTO.** Toda cifra —nota,
   instancias, multiplicador, precios— la escriben los scripts de las skills.
   Prohibido calcular números mentalmente o editarlos a mano en los JSON.
2. **Compuertas duras.** Un validador con exit 1 bloquea la etapa siguiente. Se
   corrige el archivo, jamás se relaja el contrato. Tras 3 intentos fallidos:
   detenerse y reportar los errores del validador textuales, sin parafrasear.
3. **Pureza de etapa.** La ficha registra, el diagnóstico juzga, la propuesta
   ofrece. La ficha no evalúa, el diagnóstico no propone, la propuesta no
   dibuja. La tentación de adelantar contenido significa que falta un campo:
   va en advertencias, no se cuela.
4. **No inferir en la etapa 1.** Lo que no se dijo en la sesión es
   `no_capturado`, y eso es un producto: es la agenda de la segunda llamada.
   Una ficha sin huecos es señal de invención. Los **nombres propios** son el
   caso extremo: no se adivina cómo se escribe un apellido ni se elige la
   variante que suena mejor. Se registra lo oído con sus variantes, y la
   compuerta de nombres lo pregunta antes de la etapa 2.
5. **Política comercial:** vive en `politica-comercial.json` y solo la edita
   Jaime. Si falta o está incompleta, detenerse y pedirla — nunca inventar
   precios ni tramos.
6. **Nada de HTML ni lienzos aquí.** Esta carpeta termina en `propuesta.json`.
7. **Versiones de propuesta.** Si una observación del cliente cambia el
   alcance, la propuesta nueva es `-v2`; la anterior **nunca se edita ni se
   borra** (el expediente del cliente es su historial).
8. Leer el SKILL.md completo de cada etapa antes de ejecutarla, incluidas sus
   trampas conocidas. No trabajar de memoria.

---

## Estructura (híbrida: código aquí, datos en OneDrive)

**En este repo (se edita solo por commit):**
- `.claude/skills/` — las tres etapas con sus contratos, ejemplos y validadores
- `.claude/commands/diagnostico.md` — el flujo como comando de Claude Code
- `libreria/componentes.json` — librería compilada (regenerable desde los módulos)
- `ejemplos/expediente-activos/` — un caso terminado de referencia (ficha,
  diagnóstico y propuesta reales)

**En OneDrive, carpeta compartida `despegue-operacion` (los datos, editables por
el equipo):**
- `clientes/<cliente>/entrada|salida/` — un expediente por cliente
- `politica-comercial.json` — precios base, tramos, tope de descuento (solo Jaime)
- `config-acceso.json` — URL del repo y token de solo-lectura para clonar

**El repo ignora `clientes/`** (está en `.gitignore`). Cuando el pipeline corre
en un sandbox crea `clientes/<cliente>/entrada|salida/` con la transcripción y
los JSON del expediente: eso es dato de cliente —nombres, teléfonos, cifras del
negocio— y vive en OneDrive, nunca versionado aquí. El único expediente que sí
está en el repo es `ejemplos/expediente-activos/`, el caso de referencia
acordado. Si un expediente aparece en `git status`, es un error: se saca del
repo, no se commitea.

Si una observación del cliente cambia el alcance, la propuesta nueva es `-v2`;
la anterior **nunca se edita ni se borra**.
---

## Ejecución híbrida (GitHub + OneDrive + sandbox)

Cuando esta carpeta se ejecute desde un chat o Cowork SIN acceso directo de
ejecución sobre OneDrive, el patrón es:

1. **Traer el pipeline de GitHub al sandbox** (el repo es la fuente de verdad
   del código y los contratos):
   `git clone <URL-del-repo> pipeline && cd pipeline` — o descargar el zip del
   repo y descomprimirlo. Si el repo es privado, el token de solo-lectura está en
   `despegue-operacion/config-acceso.json` del OneDrive compartido.
2. **Traer la transcripción de OneDrive al sandbox** con el conector
   Microsoft 365: buscarla en `despegue-operacion/clientes/<cliente>/entrada/`.
3. **Correr las tres etapas en el sandbox** siguiendo la sección "Cuando el
   usuario pida corre el diagnóstico" tal cual (los validadores de Python
   corren localmente en el sandbox).
4. **Subir los resultados a OneDrive** con el conector: los tres JSON a
   `despegue-operacion/clientes/<cliente>/salida/`. El OneDrive es el expediente
   que ve el equipo; el sandbox es efímero y se descarta.

Reglas del híbrido:
- El código y los contratos NUNCA se editan en OneDrive: se editan en el repo
  (commit) y la siguiente sesión los trae. OneDrive solo lleva transcripciones,
  expedientes y `politica-comercial.json`.
- `politica-comercial.json` vive en `despegue-operacion/` (OneDrive) (lo edita el humano sin tocar
  Git): traerlo al sandbox junto con la transcripción antes de la etapa 3.
- Verificar SIEMPRE tras clonar: compilar la librería y comparar el hash con
  el registrado abajo. Hash distinto = repo desactualizado o rama equivocada:
  detenerse y avisar.

---

## Mantenimiento

**Actualizar la librería** (cuando cambien los `modulo-*.md`): reemplazarlos en
`.claude/skills/seleccion-propuesta/references/modulos/` y recompilar:

    python3 .claude/skills/seleccion-propuesta/scripts/compilar_libreria.py \
      .claude/skills/seleccion-propuesta/references/modulos libreria/componentes.json

Debe reportar el total y un hash de versión. Ese hash queda registrado en cada
propuesta: es lo que permite saber si una propuesta vieja se hizo con librería
vieja. Estado actual: **82 componentes, hash `429593a761`, distribución 30
fundamental / 29 avanzado / 22 inteligente**, más un componente sin plan (la
integración de plataforma propia — correcto por V11: lo no nativo no viaja
dentro del plan).

Estado anterior: 81 componentes, hash `639f4fc256`, 30/29/21. El salto lo
produjo la corrección C2 del catálogo de habilidades IA, que dividió
`gestion-chatbot-precalificacion` en `gestion-asistente-informativo`
(avanzado) y `gestion-precalificador` (inteligente). **Las propuestas emitidas
contra `639f4fc256` referencian dos ids que ya no existen** —el dividido y
`reactivacion-precalificacion-ia`, renombrado por C4—: validarlas contra la
librería nueva falla, y eso es exactamente para lo que el hash está en cada
propuesta. Una propuesta vieja no se edita (regla 7): si su alcance sigue
vigente se emite `-v2` contra la librería nueva.

**Carpeta compartida:** esta carpeta vive en OneDrive compartido. La librería y
la política son únicas y compartidas a propósito — nadie trabaja sobre copias
sueltas, porque las copias derivan.
