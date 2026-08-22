# Pipeline comercial Ropofy

Esta carpeta convierte transcripciones de demos comerciales y de sesiones
estratégicas en archivos validados, mediante skills encadenadas con compuertas
de validación. Cadena completa: demo comercial (E0) → `prospecto.json` +
`qa-demo.json` → sesión estratégica (E1) → `ficha.json` → `diagnostico.json`
(E2) → `propuesta.json` (E3) → blueprint (E4, contrato sin skill todavía).
El renderizador del lienzo es otra aplicación y consume el `propuesta.json`
que aquí se produce.

---

## Cómo se usa (el consultor)

1. Crear `clientes/<cliente>/entrada/` y soltar ahí la(s) transcripción(es),
   con fecha en el nombre: `2026-08-14-sesion-1.docx`. Las de demo comercial
   llevan sufijo `-demo`: `2026-08-14-demo.docx`.
2. Decir: **"procesa la demo de <cliente>"** (tras la demo de venta) o
   **"corre el diagnóstico de <cliente>"** (tras la sesión estratégica).
3. Recoger los JSON en `clientes/<cliente>/salida/` y la agenda que se entrega
   al final (del diagnóstico si fue demo; de la segunda llamada si fue sesión).

`<cliente>` es un nombre corto sin espacios ni tildes: `activos`, `ayc`.

**Enrutamiento cuando el nombre del archivo no lo dice:** una demo comercial
sigue el guion de 13 bloques, muestra la plataforma y habla de precios; una
sesión estratégica diagnostica sin vender. En caso de duda, preguntar antes de
correr nada — extraer una demo con la skill de la etapa 1 produce una ficha
falsa, y viceversa.

---

## Cuando el usuario pida "procesa la demo de <cliente>"

Es la **etapa 0** (`extraccion-demo`). Corre completa, sin paradas
interactivas (los nombres propios de la demo viajan en el prospecto con su
`confianza`; la compuerta de nombres es de la etapa 1).

1. Lee `.claude/skills/extraccion-demo/SKILL.md` y su contrato
   (`references/schema-prospecto.md`) completos.
2. Extrae el texto de la transcripción de demo de `clientes/<cliente>/entrada/`
   (docx → texto plano). Antes de extraer, resuelve lo de `_meta`: cuántos
   hablantes reales hay y **dónde termina la demo efectiva** (hay grabaciones
   que siguen horas; ese audio ambiente no se procesa como demo).
3. Escribe `clientes/<cliente>/salida/prospecto-<cliente>-<fecha>.json`.
   Reglas madre: lo no dicho = `no_capturado` con su motivo de ausencia, y
   **todo dato lleva fuente** — lo que afirmó la ejecutiva o se supuso para
   cotizar es hipótesis, nunca dato del cliente.
4. COMPUERTA:

       python3 .claude/skills/extraccion-demo/scripts/validar_prospecto.py \
         clientes/<cliente>/salida/prospecto-<cliente>-<fecha>.json

5. Con el prospecto validado, genera el QA (los scores los escribe el script,
   nunca el modelo):

       python3 .claude/skills/extraccion-demo/scripts/qa_demo.py \
         clientes/<cliente>/salida/prospecto-<cliente>-<fecha>.json \
         -o clientes/<cliente>/salida/qa-demo-<cliente>-<fecha>.json

6. **Entrega final, siempre en este formato:**
   1. Tabla de los dos archivos con su ruta y su línea de validación.
   2. `agenda_diagnostico` priorizada: bloqueantes primero, luego altas.
   3. El **brief previo listo para WhatsApp**: solo los ítems con
      `momento: brief_previo`, redactados como mensaje, excluyendo todo lo que
      el cliente ya declaró en la demo.
   4. `bloqueos_para_avanzar` y las hipótesis a verificar en pantalla.
   5. Resumen del QA: score global, semáforo, top-3 acciones de coaching. Las
      advertencias del validador se reportan textuales (algunas señalan errores
      comerciales de la demo, no de extracción — para eso existen).

Variante — **"dame el QA de la demo de <cliente>"**: si ya existe el
`prospecto.json` en `salida/`, corre solo `qa_demo.py` sobre él; no re-extraigas.

Variante — **"dame el brief previo de <cliente>"**: si ya existe el prospecto,
genera solo el punto 3 de la entrega; si no existe, primero procesa la demo.

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
en una sola ficha). Convierte los .docx a texto plano primero.

**Si existe `prospecto-<cliente>-*.json` en `salida/`, es la semilla:** sus
datos con fuente `cliente_declaro`/`cliente_confirmo` entran a la ficha como
pre-capturados (con su evidencia, citando la demo como fuente) y en la sesión
solo se confirman; sus `hipotesis_a_verificar` se contrastan contra lo que la
sesión diga; su `agenda_diagnostico` es el checklist de cobertura — un ítem
`bloqueante` del prospecto que la sesión no resolvió va destacado en la agenda
de la segunda llamada. Nunca registrar como dato de la sesión algo que solo se
dijo en la demo. Valida:

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
3. **Pureza de etapa.** El prospecto registra la demo, la ficha registra la
   sesión, el diagnóstico juzga, la propuesta ofrece. Ninguna etapa adelanta
   el contenido de la siguiente: la tentación de hacerlo significa que falta
   un campo — va en advertencias, no se cuela.
4. **No inferir en las etapas de extracción (0 y 1).** Lo que no se dijo es
   `no_capturado`, y eso es un producto: la agenda del diagnóstico (E0) o de
   la segunda llamada (E1). Un archivo sin huecos es señal de invención.
   En el prospecto rige además la **procedencia**: un dato con fuente
   `ejecutivo_*`, `cliente_asintio` o `cliente_forzado_por_menu` es hipótesis
   y nunca se propaga a la ficha como dato del cliente.
   Los **nombres propios** son el
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
- `.claude/skills/` — las etapas con sus contratos, ejemplos y validadores:
  `extraccion-demo` (E0, con el QA y dos guiones: **v4.1 es el vigente** —19
  bloques— y v3 queda como referencia de auditoría para demos anteriores),
  `extraccion-diagnostico` (E1), `evaluacion-modular` (E2),
  `seleccion-propuesta` (E3) y `especificacion-blueprint` (E4, solo contrato)
- `.claude/commands/diagnostico.md` y `.claude/commands/demo.md` — los flujos
  como comandos de Claude Code
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
2. **Traer los insumos de OneDrive al sandbox** con el conector
   Microsoft 365: la transcripción desde
   `despegue-operacion/clientes/<cliente>/entrada/` y, para un diagnóstico,
   también el `prospecto-<cliente>-*.json` de `salida/` si existe (semilla de
   la etapa 1) y `politica-comercial.json`.
3. **Correr la(s) etapa(s) en el sandbox** siguiendo la sección que
   corresponda ("procesa la demo" o "corre el diagnóstico") tal cual (los
   validadores de Python corren localmente en el sandbox).
4. **Subir los resultados a OneDrive** con el conector: los JSON producidos a
   `despegue-operacion/clientes/<cliente>/salida/`. El OneDrive es el expediente
   que ve el equipo; el sandbox es efímero y se descarta.

Reglas del híbrido:
- El código y los contratos NUNCA se editan en OneDrive: se editan en el repo
  (commit) y la siguiente sesión los trae. OneDrive solo lleva transcripciones,
  expedientes y `politica-comercial.json`.
- **Las skills instaladas en la cuenta de Claude son LANZADORES, no
  implementaciones.** No contienen contratos, scripts ni lógica: solo disparan
  el flujo (leer `config-acceso.json`, clonar este repo, ejecutar la skill
  real desde `.claude/skills/` del clon). Nunca instalar en la cuenta una
  skill con lógica: la lógica entra por commit aquí y el lanzador no cambia.
  Si un lanzador y el repo parecen contradecirse, manda el repo. (La regla
  existe porque las copias completas derivaron en ambas direcciones y hubo
  que reconciliarlas: ficha v0.3 vivía solo en el repo; propuesta v0.5 y
  diagnóstico v0.2 vivían solo en la cuenta.)
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
vieja. Estado actual: **88 componentes, hash `f92c2bb130`, distribución 32
fundamental / 30 avanzado / 24 inteligente**, más **dos** componentes sin plan
(la integración de plataforma propia y la impresión térmica de la comanda —
correcto por V11: lo no nativo no viaja dentro del plan).

El salto desde `f1f8871e22` (82 componentes, 30/28/23) lo produjo la familia de
**Cierre de ciclo corto**: cinco componentes nuevos para el negocio donde el
cierre y el primer contacto son el mismo momento (confirmación de pedido,
estados del pedido, despacho por sector, aviso de avance, alerta de pedido
estancado) más la impresión de comanda al carril. En la misma tanda, los cinco
componentes de cierre formal ganaron un `aplica_si` que los excluye solos donde
no hay cotización ni firma.

Cómo se llegó aquí desde `639f4fc256` (81 componentes, 30/29/21):

- La corrección **C2** del catálogo de habilidades IA dividió
  `gestion-chatbot-precalificacion` en `gestion-asistente-informativo`
  (avanzado) y `gestion-precalificador` (inteligente) — de ahí el componente
  extra. La **C4** renombró `reactivacion-precalificacion-ia` a
  `reactivacion-absorcion-oleadas`.
- Los once `aplica_si` del módulo Cierre pasaron a apoyarse en
  `linea.emite_documento_formal` (ficha v0.4) en vez de en `ciclo_dias`. No
  cambia ningún componente ni ningún plan — cambia la condición, que es campo
  compilado, y por eso el hash se mueve.
- `nutricion-encuesta-recalificacion` subió de avanzado a **inteligente**: se
  dispara tras la secuencia de no-respuesta, o sea por ausencia de acción, que
  es la prueba de pertenencia de Inteligente. Eso mueve un componente entre
  columnas y cierra una violación V1 que traía la librería.

**Las propuestas emitidas contra un hash anterior referencian ids que ya no
existen** y eso ya no rompe nada: cada propuesta declara su `libreria_hash`
(schema de propuesta §9) y el validador la reconoce como *histórica* — valida
estructura, aritmética y herencia, y sale 0 con advertencia. Una propuesta
vieja no se edita (regla 7): si su alcance sigue vigente, se emite `-v2`
contra la librería nueva.

**Carpeta compartida:** esta carpeta vive en OneDrive compartido. La librería y
la política son únicas y compartidas a propósito — nadie trabaja sobre copias
sueltas, porque las copias derivan.
