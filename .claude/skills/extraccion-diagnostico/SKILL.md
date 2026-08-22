---
name: extraccion-diagnostico
description: Extrae la ficha de perfil de cliente (ficha.json) desde transcripciones de sesiones estratégicas de diagnóstico comercial de Ropofy. Usar siempre que el usuario suba una transcripción de sesión (docx/txt de Teams, Meet o similar) y pida procesarla, extraer la ficha, "correr la etapa 1", diagnosticar un cliente nuevo, o preparar insumos para una propuesta — incluso si solo dice "procesa esta sesión" o "aquí está la llamada con [cliente]". Es la primera etapa de la cadena diagnóstico → propuesta y ninguna etapa posterior puede correr sin ella.
---

# Etapa 1 — Extracción de diagnóstico a ficha

Convierte transcripciones crudas de la sesión estratégica en una `ficha.json`
que cumple el contrato `references/ficha-perfil-cliente.md`. La ficha alimenta
las etapas 2 (evaluación) y 3 (selección de componentes): un error aquí se
propaga a la propuesta que el cliente firma.

## La regla madre: NUNCA inferir

Esta skill produce un registro de **lo que se dijo**, no una interpretación de
lo que probablemente sea cierto.

- Dato dicho en la sesión → se registra con su evidencia textual.
- Dato no dicho → `"no_capturado"`. Jamás se completa con conocimiento del
  sector, con lo típico, ni con lo que "seguramente" aplica.
- Dato dicho a medias o ambiguo → se registra lo dicho y se marca la duda en
  el mismo campo: `"~100/día (dijo 'como cien, a veces más')"`.

Por qué es absoluta: los `no_capturado` **son un producto**, no un defecto. Su
lista es la agenda de la segunda llamada del consultor. Una ficha sin huecos de
una sesión de 60 minutos es señal de invención, no de calidad.

## Proceso

1. **Leer el contrato primero**: `references/ficha-perfil-cliente.md` define
   cada bloque (A–F), sus campos y sus valores válidos. Es la única fuente de
   estructura; no agregar campos que no existan en él.
2. **Leer las transcripciones completas** (puede haber más de una sesión del
   mismo cliente; se consolidan en una sola ficha). Si el archivo es .docx,
   extraer el texto con las herramientas del entorno.
3. **Primera pasada — actores**: identificar cada persona que habla, su cargo
   declarado y su función canónica (asesor, coordinador, captador, sistema,
   habilitador_de_activo, externo_afiliado…). Registrar también las funciones
   **mencionadas pero ausentes** de la reunión (`funciones_sin_representacion`):
   son dueñas de procesos que se diseñarán sin ellas.
4. **Segunda pasada — bloques A–F** en orden. Para cada dato registrado,
   guardar la **cita textual** que lo respalda en el campo `evidencia`
   (recortada, ≤ 200 caracteres, con comillas españolas «»).
5. **Tercera pasada — calidad del diagnóstico (bloque F)**: es el bloque que
   más se olvida y el que más protege al consultor. Verificar uno a uno:
   datos económicos capturados (define `modo_propuesta` A o B),
   `datos_en_conflicto`, `decisor_presente`, `base_legal_contacto`.
6. **Salida**: un único archivo `ficha-<cliente>.json`, UTF-8, con el bloque
   `_meta` (fuentes, fecha, versión de ficha, `marca` y `razon_social` con su
   grafía y su estado). Entregarlo como archivo, no pegado en la conversación.
7. **Compuerta de confirmación de nombres propios**: se corre después de que
   `validar_ficha.py` sale con 0 y **antes** de devolver el control a la etapa 2.
   Es la única parada de la cadena que le pregunta algo al consultor. Ver
   §Compuerta.

## Compuerta de confirmación de nombres propios

El contrato (desde v0.3) da dónde **registrar** que una grafía está por confirmar. Esta
compuerta es lo que la **resuelve**: sin ella la duda queda escrita y nadie la
levanta, y una grafía equivocada llega intacta al lienzo que el cliente lee.

**Cuándo corre.** Después de `validar_ficha.py` con exit 0, antes de devolver el
control a la etapa 2. No antes de entregar la ficha, y no al final del pipeline:
al cierre de la etapa 1 la corrección **se propaga sola** a diagnóstico y
propuesta, porque todavía no existen. Si la compuerta estuviera al final,
corregir un apellido obligaría a rehacer los tres archivos.

**Qué muestra.** Una sola tabla con TODOS los nombres propios de la ficha —razón
social, marca, cada persona de `personas_declaradas`, cada sistema de
`D_stack.sistemas`— cada uno con su grafía propuesta, su estado y las variantes
literales de la transcripción **sin corregir**:

```
| # | qué es                        | grafía propuesta      | estado        | variantes en la transcripción                          |
|---|-------------------------------|-----------------------|---------------|--------------------------------------------------------|
| 1 | razón social                  | BIFTEKI S.A.S.        | por confirmar | «Bifteki» · «BIFTEKI S.A.S.»                           |
| 2 | marca                         | Gosen casa de Comidas | por confirmar | «Gocé en casa de comidas» · «G o SEN casa de comidas»   |
| 3 | persona · telefonista         | Sharina               | por confirmar | «Sharina» · «Yanina» · «¿Te dices Danina?»              |
| 4 | sistema · gestión del local   | Pixo Gestión          | por confirmar | «It's pizza» · «BXO» · «Pitso» · «Bitso»                |
```

Y una sola pregunta: **para cada fila, ¿confirmas la grafía y dónde la viste
escrita, la corriges, o la dejas por confirmar?**

**Qué se hace con la respuesta.**

| respuesta del consultor | qué se escribe en la ficha |
|---|---|
| **La confirma** | el estado pasa a `confirmada` y se registra **cómo** se confirmó en `fuente_escrita`: correo, firma, factura, sitio, contrato, documento compartido. Sin fuente concreta no se cierra el estado — el validador lo bloquea (I5). |
| **La corrige** | se reescribe la grafía (y `_meta.cliente` si era la marca: van juntos o el validador falla en I1), el estado pasa a `confirmada` con su `fuente_escrita`, y **las variantes se conservan** como rastro de dónde salió el error. Nunca se borran. |
| **No la sabe** | queda `por_confirmar` y entra a la **agenda de la segunda llamada**, arriba: la grafía se imprime en el lienzo que el cliente va a leer. |

Aplicadas las respuestas, se reescribe la ficha y **se vuelve a correr
`validar_ficha.py`**: corregir una grafía puede romper la consistencia entre
`_meta.cliente` y `_meta.marca.grafia`. Recién ahí sigue la etapa 2.

**Qué NO hace la compuerta: adivinar.** La regla de no inferir no se toca. Un
nombre que el consultor no confirma no se "arregla" ni se elige entre variantes
por lo que suene mejor: se marca. Elegir la grafía más plausible es inferir, y
sigue prohibido aquí igual que en el resto de la etapa.

**La trampa del título de la reunión.** El título de la grabación de Teams —
«Sesión estratégica Ropofy - BIFTEKI S.A.S. - Santiago Odasso»— parece fuente
escrita y es la trampa más fácil de pisar: **lo escribió quien creó la reunión,
que casi siempre es Ropofy**, no el cliente. No confirma nada; a lo sumo confirma
cómo lo escribe Ropofy. Tampoco confirman: el nombre del archivo de la
transcripción, la invitación de calendario, ni el nombre del chat. El validador
rechaza esa justificación (I6).

**Filas que no son nombres propios.** Un rol usado como nombre («Territoriales»,
«el call center») igual aparece en la tabla: ahí la pregunta es si así los nombra
el cliente. Si lo confirma, la fuente es donde esté escrito (organigrama,
contrato); si no hay dónde, queda por confirmar. No se inventa un apellido para
rellenar.

**Corrida desatendida** (tarea programada, sin humano al otro lado): la compuerta
**no bloquea**. Todo queda `por_confirmar` y la entrega lo dice en su primera
línea. Ver `CLAUDE.md` §Cuando el usuario pida "corre el diagnóstico".

## Trampas conocidas (cada una costó un error real)

**El falso conflicto.** Antes de registrar `datos_en_conflicto`, verificar que
las dos personas hablan del MISMO objeto. El contrato exige `objeto_a` y
`objeto_b`: si difieren, no es conflicto — son dos datos ciertos y ambos se
registran por separado. Caso real: "tenemos formulario" (hablaba de la pauta
de Meta) vs "no tenemos formulario" (hablaba del sitio web). Ambos tenían
razón; declararlo conflicto habría hecho quedar mal al consultor.

**El volumen sin denominador.** "Tenemos 4.000 leads" puede ser represados
acumulados o entrada mensual — son diagnósticos opuestos. Si la transcripción
no lo aclara con una repregunta del consultor, registrar la cifra con su
ambigüedad explícita, nunca elegir una interpretación.

**Números que se corrigen en la misma sesión.** La gente redondea y luego
precisa ("3.000… bueno, son 3.900"). Vale la última cifra dicha, y la
evidencia debe citar esa.

**Líneas de negocio compartiendo canal.** Si venta, arriendo, captación y
servicio entran por el mismo WhatsApp, cada una es una línea en el bloque A
con su propio `sujeto_del_embudo`, `control_del_activo` y
`mecanismo_de_cierre`. No colapsarlas porque compartan número.

**El tercero que controla el activo.** Si alguien más tiene las llaves, aprueba
el estudio, o fija el calendario (aseguradora, entidad estatal, franquiciante),
eso va en `dependencias_externas` de la línea y condiciona qué se puede
prometer. Buscarlo activamente: los entrevistados lo mencionan de pasada.

**El nombre propio que la transcripción destroza.** Teams y Meet transcriben
fonéticamente: los nombres propios —marcas, apellidos, nombres de sistemas— salen
mal y salen mal de varias formas distintas en la misma sesión. Caso real: la marca
«Gosen casa de Comidas» (Gosen es un apellido) quedó como «Gocé en casa de
comidas» y «G o SEN casa de comidas», y la ficha arrastró la grafía equivocada
hasta la propuesta que el cliente leyó. La regla de no inferir no se toca: **no se
adivina cómo se escribe un apellido**. Lo que se hace es declararlo — en
`_meta.marca`, `_meta.razon_social`, cada persona de `personas_declaradas` y cada
sistema de `D_stack.sistemas` van la grafía que se usará, el estado
(`por_confirmar`) y las variantes literales que trae la transcripción, copiadas
sin corregir. Solo se pone `confirmada` si la grafía se vio **escrita** por alguien
de la empresa (correo, firma, factura, sitio, documento compartido); oírla en la
sesión no confirma nada. Señales de que hay que revisar: el nombre aparece con dos
grafías distintas, se parte en letras sueltas, o suena a palabra común donde
debería ir un apellido. Y registrar no es suficiente: quien resuelve la duda es la
**compuerta de confirmación de nombres** al cierre de la etapa (ver §Compuerta).

**Small talk y datos personales.** Las sesiones traen charla de ciudad, clima,
familia. Nada de eso entra a la ficha salvo que sea dato operativo (la sede sí;
que el consultor sea de la misma ciudad, no).

## Checklist antes de entregar

- [ ] Todos los campos del contrato presentes; los sin dato dicen `"no_capturado"` (no vacíos, no null salvo que el contrato lo pida)
- [ ] Cada dato no obvio tiene `evidencia` textual
- [ ] `datos_en_conflicto` solo con `objeto_a` == `objeto_b`; si difieren, registrados como dos datos
- [ ] `momento_de_cobro` por línea: ¿cobra al pedir o contra entrega? Es dato de arquitectura, no de configuración — si no se preguntó, va como `no_capturado` a la agenda de la segunda llamada, no se deduce
- [ ] `modo_propuesta` = "B" si no hay ticket, margen, comisión ni ad spend
- [ ] `funciones_sin_representacion` revisado (¿quién es dueño de un proceso y no estuvo?)
- [ ] Bloque D incluye `whatsapp_estado`, `numeros_publicados`, `llamadas_medidas`, `decision_del_numero` (aunque sea todo no_capturado: la sesión vieja no los preguntaba)
- [ ] `_meta.marca` y `_meta.razon_social`, y cada persona y cada sistema, con su grafía, su estado y las variantes literales de la transcripción; `confirmada` solo con `fuente_escrita` de algo que se vio escrito
- [ ] **Compuerta de nombres corrida**: la tabla completa mostrada al consultor, sus respuestas aplicadas, la ficha reescrita y `validar_ficha.py` corrido otra vez (§Compuerta)
- [ ] Lo que quedó `por_confirmar` está arriba en la agenda de la segunda llamada — y si la corrida fue desatendida, la entrega lo dice en su primera línea
- [ ] Ninguna grafía se "arregló" adivinando: lo que el consultor no confirmó sigue marcado, no corregido
- [ ] Cero recomendaciones, cero componentes, cero juicios: esta etapa registra, no evalúa
- [ ] El JSON parsea (validarlo ejecutándolo, no a ojo)

## Referencias

- `references/ficha-perfil-cliente.md` — el contrato completo. **Leerlo siempre antes de extraer**; cambia con versión y esta skill no lo duplica a propósito.
- `examples/ficha-ejemplo-activos.json` — ficha real de un caso multilínea con tercero institucional, modo B y 9 no_capturado. Es el estándar de qué tan lejos llegar y dónde detenerse.

## Evaluación del output

Antes de entregar cualquier ficha, correr el validador automático:

```
python3 scripts/validar_ficha.py ficha-<cliente>.json [transcripcion.txt]
```

Si falla (exit 1), corregir y volver a correr — nunca entregar una ficha que no
pasa. Los criterios de juicio (los que el script no puede ver) están en
`references/criterios-evaluacion.md`; usarlos como auto-revisión final y como
guía cuando un humano audite la ficha.
