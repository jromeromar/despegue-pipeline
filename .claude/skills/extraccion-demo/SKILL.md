---
name: extraccion-demo
description: Extrae el prospecto.json desde transcripciones de demos comerciales de Ropofy (la llamada de venta consultiva previa a la Arquitectura). Usar siempre que el usuario suba la grabación o transcripción de una demo y pida procesarla, "correr la etapa 0", extraer el prospecto, auditar cómo se ejecutó el guion de la demo, o preparar las preguntas del diagnóstico de un cliente nuevo — incluso si solo dice "procesa esta demo" o "aquí está la llamada con [cliente]". Es la etapa anterior a extraccion-diagnostico y produce la agenda de preguntas que esa sesión va a usar.
---

# Etapa 0 — De la demo al prospecto

Convierte la transcripción cruda de una demo comercial en un `prospecto.json`
que cumple el contrato `references/schema-prospecto.md`.

El consumidor principal del archivo **no es un humano leyendo un resumen**: es
la skill que genera el guion de preguntas del Diagnóstico. Todo lo demás
(calificación comercial, coaching del ejecutivo, inteligencia agregada) sale del
mismo registro, pero la agenda del diagnóstico es lo que decide si el archivo
sirve.

Posición en la cadena: **demo (E0)** → `prospecto.json` → ficha.json (E1,
skill `extraccion-diagnostico`) → diagnostico.json (E2) → propuesta.json (E3)
→ blueprint.json (E4).

## Las dos reglas madre

**Nunca inferir.** Dato dicho → se registra con su evidencia textual. Dato no
dicho → `"no_capturado"` con el motivo de su ausencia. Jamás se completa con lo
típico del sector, con la plantilla de demo de esa vertical, ni con lo que
"seguramente" aplica.

**Quién lo dijo importa más que qué se dijo.** En las demos reales, una parte
grande de los "datos del cliente" los enunció el ejecutivo y el cliente solo
asintió, o fueron inventados para poder cotizar. Antes de registrar cualquier
número hay que resolver si lo declaró el cliente, lo afirmó el ejecutivo, o el
cliente lo eligió de un menú cerrado. Son tres datos distintos y el campo
`fuente` los separa. Un dato sin procedencia es una hipótesis disfrazada de
hecho, y aguas abajo nadie va a poder distinguirla.

Corolario de ambas: **los vacíos son un producto.** Su lista es la agenda de la
sesión de diagnóstico. Un prospecto sin huecos tras una demo de 30 minutos es
señal de invención, no de calidad — el validador lo advierte.

## Proceso

1. **Leer el contrato primero**: `references/schema-prospecto.md`. Define cada
   bloque, el tipo `Dato`, los enums y las reglas. Es la única fuente de
   estructura; no agregar campos que no existan en él.
2. **Leer la transcripción completa.** Si es .docx, extraer el texto con las
   herramientas del entorno. Antes de extraer nada, resolver tres cosas de
   `_meta`: cuántos hablantes reales hay (los diarizadores colapsan personas),
   qué tan sucio está el ASR, y **dónde termina la demo** — hay grabaciones que
   siguen corriendo horas después y ese audio ambiente no es parte de la demo.
3. **Primera pasada — actores y guion.** Identificar a cada persona, separar
   `nombre_en_agenda` de `nombre_en_llamada` (divergen a menudo), resolver quién
   decide el gasto, y marcar los minutos de los hitos: cuándo se compartió
   pantalla, cuándo se dijo el primer precio, cuándo se pidió cada cierre.
4. **Segunda pasada — bloques A–F** (el prospecto). Para cada dato: valor,
   unidad, fuente, hablante, minuto y cita ≤ 200 caracteres en comillas «».
5. **Tercera pasada — bloques G–I** (lo que dijo Ropofy y cómo se ejecutó).
   Comparar cada precio y plazo dicho contra el catálogo y registrar toda
   diferencia. Auditar los 13 bloques y las 5 preguntas fijas del descubrimiento.
6. **Cuarta pasada — bloque J.** Conflictos, hipótesis, vacíos y **agenda del
   diagnóstico**. Es la pasada que da valor al archivo y la que más se salta.
   Ninguna pregunta de la agenda se agrega "porque suele preguntarse": cada una
   deriva de un vacío, una hipótesis, un conflicto, una pregunta del cliente sin
   responder o un requisito declarado, y lo dice en `deriva_de`.
7. **Validar y entregar.** Un único archivo `prospecto-<cliente>-<fecha>.json`,
   UTF-8, entregado como archivo.

## Trampas conocidas (cada una salió de una demo real)

**El volumen inventado para cotizar.** Cuando el cliente no sabe cuántos leads
recibe, el ejecutivo suele poner un número para poder dar precio («supongamos 10
al día, llevémoslo al máximo»). Ese número **no es un dato del negocio**: va con
`fuente: ejecutivo_supuso_para_cotizar` y genera hipótesis. Registrarlo como
dato del cliente hace que la propuesta se dimensione sobre aire.

**El «Mhm» que parece confirmación.** Hay demos donde casi todo el diagnóstico
lo enunció el ejecutivo y el cliente asintió. Eso es `cliente_asintio`, no
`cliente_declaro`, y también es hipótesis.

**Las tres formas de no saber.** `no_preguntado` (el ejecutivo no lo indagó →
va a la agenda y cuenta como error de ejecución), `cliente_no_lo_sabe` (hallazgo
de madurez: no se pregunta, se instrumenta) y `dato_no_existe_en_el_negocio`
(cambia el eje del diagnóstico). Colapsarlas en un solo `null` destruye el
producto de esta etapa.

**`no_indagado` no es `inexistente`.** Si nadie preguntó si hay CRM, el stack
dice `no_indagado`. Escribir "no tiene CRM" produce una ficha falsa y una
migración que aparece después de firmar.

**Dos arquetipos de dolor, no uno.** El guion asume fuga por saturación, pero
hay clientes de arranque de canal: cero leads digitales, nada que perder. A esos
no se les pregunta cuántos leads pierden — se les pregunta contra qué se va a
medir el canal nuevo. El campo `arquetipo` decide el eje de la agenda.

**Cifra rota por el ASR.** «nos escriben 57310» probablemente sean «5, 7, 3,
10». Se registra con `confianza: asr_dudoso` y **nunca** se propaga como dato
limpio a la etapa 1.

**El dolor sin cuantificar.** Es lo normal, no la excepción, incluso cuando el
cliente sirvió el número en bandeja. Cada dolor con `cuantificado: false`
obliga a una pregunta de cuantificación en la agenda, con la magnitud del
negocio, no del sector.

**El falso conflicto.** Antes de registrar `datos_en_conflicto`, verificar que
las dos versiones hablan del **mismo objeto**. Si difieren, no es conflicto: son
dos datos ciertos y ambos se registran. Misma regla que en la etapa 1.

**Audio ambiente.** Si la grabación siguió corriendo, puede contener el
detonante real y el stack verdadero. Se registra con `fuente: audio_ambiente`
como contexto y **jamás** se cita ante el cliente.

**Confidencialidad al revés.** Si en la demo se nombraron otros clientes de
Ropofy o se comentó su configuración, va en
`lo_que_dijo_ropofy.informacion_de_terceros_revelada`. Es riesgo, no anécdota.

## Checklist antes de entregar

- [ ] Todo `Dato` tiene `fuente`; los de cliente/ejecutivo tienen `hablante`
- [ ] Toda cifra tiene `unidad`; `volumen_leads` tiene `tipo` y `precision`
- [ ] Toda cita va en «» y no pasa de 200 caracteres
- [ ] Cada ausencia declara su motivo (uno de los cinco)
- [ ] `hipotesis_a_verificar` recoge todo lo que el ejecutivo afirmó o supuso
- [ ] `vacios[]` completo — si tiene menos de 8 entradas en una demo de más de 20 minutos, sospechar de la extracción
- [ ] Cada entrada de `agenda_diagnostico` tiene `deriva_de`, `campo_destino`, `quien_debe_responder` y `momento`
- [ ] La habilitación Meta va como `evidencia_en_vivo`: se ve en pantalla, no se pregunta de memoria
- [ ] Los 13 bloques y las 5 preguntas fijas están auditados con su estado
- [ ] Cada precio y plazo dicho está comparado contra catálogo
- [ ] Cero recomendaciones, cero componentes, cero precios propuestos: esta etapa registra, no evalúa
- [ ] El JSON parsea y pasa el validador

## Evaluación del output

```
python3 scripts/validar_prospecto.py prospecto-<cliente>-<fecha>.json
```

Si falla (exit 1), corregir y volver a correr — nunca entregar un prospecto que
no pasa. Las advertencias no bloquean, pero hay que leerlas: algunas (como
"detonante con fecha dura y next step sin fecha") no señalan un error de
extracción sino un error comercial de la demo, y eso es exactamente lo que el
archivo existe para hacer visible.

Con el prospecto validado, generar el QA de la demo (segundo entregable):

```
python3 scripts/qa_demo.py prospecto-<cliente>-<fecha>.json
```

Produce `qa-demo-<cliente>-<fecha>.json` con score 0-100 por dimensión
(calificación, descubrimiento, conducción, precio, cierres, riesgo,
siguiente paso), semáforo y acciones de coaching. No re-lee la transcripción:
todo sale de los bloques G, H e I del prospecto, así que ambos archivos nunca
se desincronizan. El prospecto viaja al diagnóstico; el QA viaja a coaching.
Entregar ambos.

## Referencias

- `references/schema-prospecto.md` — el contrato completo con las reglas P1–P18. **Leerlo siempre antes de extraer.**
- `references/guion-demo-v4.1.md` — **el guion vigente** (consultivo con capa de riesgo, fusión V4 de Mariana + reinjertos del V3). Audita 19 bloques (`0, 1.1–1.5, 2–11, FT, 12, 13`) cuando `version_guion` es "Guion Demo v4.1 / consultivo".
- `references/guion-demo-v3.md` — referencia histórica: audita 13 bloques para demos ejecutadas con el v3. Para demos anteriores a ambos, auditar contra el guion v2026 (también 13).
- El mapa canónico de bloques por versión vive en `GUION_BLOQUES` dentro de `scripts/validar_prospecto.py`: si cambia el guion, se actualiza ahí o la regla P13 audita contra el mapa equivocado.
- `examples/prospecto-drogueria-rr-20260803.json` — arquetipo *arranque de canal*: cero digital, decisor presente, comparación activa de proveedores, modo B. Es el caso que muestra por qué el descubrimiento del guion no aplica tal cual.
- `examples/prospecto-american-20260803.json` — arquetipo *fuga con expansión comprometida*: detonante contractual con fecha dura, decisor ausente, objeción técnica sobre una línea de 25 años, cotización improvisada. Es el estándar de cuánta agenda produce una demo bien extraída (22 preguntas).
