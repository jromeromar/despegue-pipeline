# Schema `prospecto.json` — Etapa 0: de demo comercial a insumo del diagnóstico

Contrato de datos v0.1.1 (19-ago-2026).
v0.1.1: `ejecucion_del_guion.bloques[]` deja de ser una lista fija de 13 y
pasa a validarse contra el **mapa canónico de la versión de guion declarada**
en `_meta.version_guion` — v2026 y v3 auditan 13 bloques (ids 1–13); el
**Guion v4.1** audita 19 (`0, 1.1–1.5, 2–11, FT, 12, 13`). El mapa vive en
`GUION_BLOQUES` dentro de `scripts/validar_prospecto.py`. Sin otro cambio de
estructura: los prospectos v0.1 existentes siguen siendo válidos.

**Posición en la cadena:** **demo (E0)** → `prospecto.json` → ficha.json (E1) →
diagnostico.json (E2) → propuesta.json (E3) → blueprint.json (E4).

**Corpus de calibración:** 10 demos reales de Mariana Castaño, jul–ago 2026,
14–57 min: *(Bifteki)* comidas rápidas AR · *(Dra Age)* medicina estética CO ·
*(Astrid)* agencia de viajes · *(Jenny)* inmobiliaria PE · *(Droguería)* farmacia
retail CO · *(Megafoto)* impresión fotográfica CO · *(FunProtect)* educación
técnica CO · *(NūT)* decoración mayorista AR · *(Nicolás)* B2B con HubSpot ·
*(American)* centro de idiomas CO. Cada decisión de diseño se cita con el caso
que la obligó. **Ningún campo de este schema existe sin evidencia de haber
aparecido —o de haber faltado de forma sistemática— en ese corpus.**

---

## 0. Qué es y qué no es este documento

`prospecto.json` es el **registro estructurado de una demo**. Su consumidor
principal es la skill que genera el **guion de preguntas del Diagnóstico**
(la sesión estratégica de la Arquitectura Comercial). De ahí se derivan tres
consecuencias de diseño que gobiernan todo lo demás:

**D1 — Lo que ya se dijo no se vuelve a preguntar; se confirma.** Cada dato
capturado viaja con su evidencia textual para que el guion del diagnóstico lo
traiga pre-llenado y solo lo valide. Preguntar dos veces erosiona la autoridad
del proceso (misma regla que E4 §1).

**D2 — Los vacíos son el producto, no el defecto.** El bloque `agenda_diagnostico`
(§J) es la razón de ser del archivo. Un prospecto sin huecos después de una demo
de 30 minutos es señal de invención.

**D3 — Un dato sin procedencia es una hipótesis disfrazada de hecho.** En el
corpus, buena parte de los "datos del cliente" los enunció la ejecutiva y el
cliente solo respondió «Mhm» *(Astrid: el 80 % del diagnóstico lo dijo la
ejecutiva)*, o fueron directamente inventados para poder cotizar *(FunProtect:
«no te lo voy a dejar con 500 lits acá»; Dra Age: 350 y luego 300 leads en dos
minutos; American: «Supongamos 10 al día… llevámoslo al máximo»)*. Sin `fuente`
por dato, el diagnóstico arrancaría verificando supuestos propios como si fueran
declaraciones del cliente.

Lo que este schema **no** hace: no evalúa fugas, no calcula madurez, no
selecciona componentes, no cotiza. Eso es E2 y E3. Aquí se registra.

---

## 1. El tipo `Dato` — envoltura universal

Todo valor sustantivo del prospecto se registra con esta forma. No es
ceremonia: es lo que separa el registro de la ficción.

```json
{
  "valor": 6,
  "unidad": "sedes",
  "fuente": "cliente_declaro",
  "hablante": "Diego Cárdenas",
  "minuto": "02:14",
  "evidencia": "«tiene 6 farmacias aquí en Granada Meta»",
  "confianza": "alta",
  "ausencia": null
}
```

| Campo | Tipo | Regla |
|---|---|---|
| `valor` | any | El dato, en la unidad del cliente. `"no_capturado"` cuando no hay dato. |
| `unidad` | texto? | Obligatoria en todo número: `leads/dia`, `pedidos/turno`, `USD/mes`, `soles`, `sedes`. *(Bifteki: «30… 50 por turno… 100 por día» — sin unidad el dato es inservible.)* |
| `fuente` | enum | Ver abajo. **Obligatoria siempre**, incluso en ausencias (`"n/a"`). |
| `hablante` | texto? | Quién lo dijo. Obligatorio si `fuente` empieza por `cliente_` o `ejecutivo_`. |
| `minuto` | `mm:ss`? | De la transcripción. Habilita la auditoría de ejecución (§I) y el "¿en qué minuto se dio el precio?". |
| `evidencia` | texto? | Cita literal ≤ 200 caracteres, comillas españolas «». Obligatoria en todo dato no obvio. |
| `confianza` | enum | `alta` · `media` · `baja` · `asr_dudoso`. `asr_dudoso` es para cifras que el transcriptor rompió *(Bifteki: «aproximadamente 3000 son 500»; NūT: «22 o 13» usuarios)*. Una cifra `asr_dudoso` **nunca** se propaga a E1 como dato limpio. |
| `ausencia` | enum? | Obligatoria si `valor == "no_capturado"`. Ver §1.2. |

### 1.1 Enum `fuente`

| Valor | Significado |
|---|---|
| `cliente_declaro` | El cliente lo dijo por iniciativa propia o respondiendo una pregunta abierta. El único dato de calidad plena. |
| `cliente_confirmo` | El ejecutivo lo afirmó y el cliente lo ratificó con palabra propia («Exactamente», «Así es»). |
| `cliente_asintio` | El ejecutivo lo afirmó y el cliente hizo «Mhm» / «Okay». **Vale como hipótesis, no como dato** *(Astrid: casi todo el perfil se construyó así)*. |
| `cliente_forzado_por_menu` | El cliente dijo "no tengo el dato" y luego eligió de un menú cerrado del ejecutivo *(Jenny: «no tengo los datos» → «menos de 500, menos de 100» → «500 por ahí»)*. Confianza `baja` obligatoria. |
| `ejecutivo_afirmo_sin_confirmar` | Lo dijo Ropofy y nadie lo validó *(Nicolás: se dio por verificado su estatus de API sin comprobarlo)*. |
| `ejecutivo_supuso_para_cotizar` | Placeholder numérico inventado para poder dar precio. **Nunca es dato del negocio**; va a `hipotesis_a_verificar`. |
| `formulario_previo` | Formulario de contacto o pre-brief. Puede estar mal *(FunProtect: llegó registrado como Universidad de La Rioja; Droguería: el formulario decía "salud y belleza" para 6 droguerías; Jenny: "construcción" para una intermediadora)*. |
| `bot_ia_ropofy` | Conversación previa del prospecto con el asistente de Ropofy. |
| `crm_precall` | Registro previo en el CRM de Ropofy. |
| `audio_ambiente` | Grabación que siguió corriendo tras la demo *(Jenny: 2 h 24 min de oficina abierta revelaron el detonante real —campañas caídas y rotación— y el Excel operativo)*. Registrable como contexto; **jamás** citable ante el cliente. |
| `inferido_de_transcripcion` | Deducción del extractor (país por la tarifa Meta usada, dueño por hablar en primera persona). Exige `nota_de_inferencia`. |
| `n/a` | Solo en ausencias. |

### 1.2 Enum `ausencia` — las cinco formas de no saber

Esta es la distinción más valiosa del schema. En el corpus, **ticket, margen y
tasa de cierre están ausentes en 10/10** — pero por razones distintas, y la
razón es lo que decide qué hace el diagnóstico con el hueco.

| Valor | Qué pasó | Qué hace el diagnóstico |
|---|---|---|
| `no_preguntado` | El guion lo pide y el ejecutivo no lo indagó. **Es el caso dominante.** | Va a `agenda_diagnostico` con prioridad alta. Y cuenta como error de ejecución (§I). |
| `preguntado_sin_respuesta` | Se preguntó y el cliente esquivó o la respuesta se perdió (típico de preguntas apiladas: *Astrid, «manejan un CRM. ¿Lo han manejado? ¿Cuántas líneas de WhatsApp tienen?»* → solo respondió lo último). | Se re-pregunta, **de una en una**. |
| `cliente_no_lo_sabe` | El cliente reconoce no tener el dato *(Dra Age: «no tenemos un aproximado porque hasta hace 15 días estamos en Doctora Age»)*. | No es hueco de la demo: es **hallazgo de madurez**. El diagnóstico no pregunta, mide o instrumenta. |
| `dato_no_existe_en_el_negocio` | Estructuralmente no hay qué capturar *(Droguería: 0 leads digitales, «todos estamos en puntos físicos»; FunProtect: «el marketing digital está muerto»)*. | El diagnóstico cambia de eje: no hay fuga que medir, hay canal que construir. |
| `no_aplica` | El campo no corresponde a este negocio. | Se omite del guion. |

**Regla P1:** `valor == "no_capturado"` ⟺ `ausencia != null`. Nunca ambos, nunca
ninguno. **Regla P4:** todo dato con `ausencia == no_preguntado` en un campo
marcado `⚑agenda` en este contrato tiene que aparecer en `vacios[]` y generar
una entrada en `agenda_diagnostico`. La lista operativa de campos ⚑agenda vive
en `CAMPOS_AGENDA` dentro de `scripts/validar_prospecto.py`: si este contrato
marca un campo nuevo, hay que agregarlo allí o la regla no se aplica.

---

## 2. Estructura de alto nivel

```
prospecto.json
├── _meta                    Trazabilidad de la extracción y calidad de la fuente
├── A. identidad             Empresa, interlocutores, decisor, ausentes
├── B. origen_y_detonante    Cómo llegó, por qué ahora, contra quién competimos
├── C. negocio               Líneas, modelo, economía (semilla del bloque A de la ficha)
├── D. operacion_actual      Canales, volumen, equipo, stack, WhatsApp, habilitación Meta
├── E. dolores_y_requisitos  Dolores con cita, requisitos funcionales, restricciones
├── F. reaccion_a_la_demo    Módulos, preguntas del cliente, objeciones, señales
├── G. lo_que_dijo_ropofy    Cotización, promesas, desviaciones, entregables ← auditoría
├── H. cierres_y_resultado   Momentos de cierre, filtro técnico, ruta, next step
├── I. ejecucion_del_guion   QA por bloque, preguntas fijas, métricas, errores
└── J. calidad_y_agenda      Conflictos, hipótesis, vacíos, AGENDA DEL DIAGNÓSTICO
```

Los bloques A–F describen **al prospecto**. G–I describen **la llamada** (y son
material de coaching, no de cliente). J es **el output que consume la etapa 1**.
Separarlos no es estética: mezclar "lo que el cliente tiene" con "lo que Ropofy
dijo que costaba" es cómo un supuesto de cotización termina viajando a la
propuesta como si fuera un hecho del negocio.

---

## 3. `_meta`

| Campo | Tipo | Notas |
|---|---|---|
| `id_prospecto` | slug | `demo-<cliente>-<yyyymmdd>` |
| `version_schema` | texto | `"0.1"` |
| `version_guion` | texto | Guion contra el que se audita: `"Guion Demo v2026 / genérico"`, `"…/ Nuevo Despegue Arquitecto"`, `"Guion Demo v3 / maestro"` o `"Guion Demo v4.1 / consultivo"`. Determina el mapa canónico de bloques de §I (regla P13); auditar contra el guion equivocado invalida §I. |
| `fuentes[]` | [objeto] | `{ archivo, tipo: transcripcion\|formulario\|crm\|chat_bot, fecha }` |
| `fecha_demo` | ISO | |
| `ejecutivo` | texto | |
| `duracion_grabacion_min` | número | |
| `duracion_demo_efectiva_min` | número | **No son lo mismo** *(Jenny: 3 h 02 de grabación, 38 min de demo; el resto es audio ambiente)*. Todas las métricas de §I corren sobre la efectiva. |
| `calidad_transcripcion` | objeto | `{ diarizacion_confiable: bool, n_hablantes_detectados, n_hablantes_reales, ruido_asr: bajo\|medio\|alto, tramos_no_utilizables[] }`. *(Megafoto: el diarizador colapsó a David y Miguel en una sola etiqueta — sin este flag, las citas se atribuyen mal.)* |
| `extraido_por` | texto | Skill y versión. |

---

## A. Identidad

### `empresa`

| Campo | Tipo | Notas |
|---|---|---|
| `nombre_comercial` | Dato | ⚑agenda. **Ausente o solo en el título del calendario en 5/10** *(NūT, Astrid, Nicolás, American, Jenny: nunca se pronuncia en la llamada)*. Si sale del título del archivo, `fuente: crm_precall`, no `cliente_declaro`. |
| `razon_social` | Dato | ⚑agenda. 0/10. |
| `es_persona_natural` | Dato(bool) | *(Droguería: «Diego Cárdenas, como tal, como persona natural, tiene 6 farmacias».)* Cambia la facturación y el contrato. |
| `vertical` | Dato | Enum abierto; el valor debe ser el del cliente, no el de la plantilla de demo. |
| `vertical_en_formulario` | Dato | Lo que decía el formulario. |
| `discrepancia_vertical` | bool + nota | **3/10 discrepan.** Es un dato de calidad del embudo propio de Ropofy, y arruina la demo cuando la ejecutiva abre con la clasificación equivocada *(FunProtect: «ya nos habías comentado que ustedes son la Universidad de La Rioja» → «No. Perdón, te corrijo…»)*. |
| `etapa_del_negocio` | Dato | `pre_operativa` · `arranque` · `en_operacion` · `en_expansion` · `en_reestructuracion`. *(Dra Age: «tenemos 2 semanas»; NūT: «estoy en la etapa inicial».)* Determina si existe línea base medible. |
| `pais` / `ciudad` | Dato | `pais` es **obligatorio con valor**: define la tarifa Meta que se cotiza (AR 0,0649 / CO 0,0131 / PE 0,07 en el corpus). Si no se dijo, se infiere de la tarifa usada y se marca `inferido_de_transcripcion`. |
| `sedes[]` | [objeto] | `{ nombre_o_ciudad, estado: activa\|abriendo\|reapertura\|proyectada, evidencia }`. *(American: Zipaquirá activa, Bogotá y Cundinamarca abriendo, Bucaramanga por convenio, Barranquilla reapertura.)* |
| `expansion_declarada` | Dato | Territorio objetivo *(NūT: «CABA → provincias»)*. |

### `interlocutores[]`

| Campo | Notas |
|---|---|
| `nombre_en_agenda` / `nombre_en_llamada` | **Se separan porque divergen en 4/10.** *(Dra Age: la cuenta dice Juan Manuel, habla la médica dueña; American: agenda "Juan Sánchez", el hablante es "Carlos"; Jenny: la ejecutiva alternó Jenny/Mayra/"Jenny Mayra" 38 minutos.)* |
| `identidad_confirmada` | bool. False en 4/10. |
| `cargo` | Dato. ⚑agenda. Explícito en 1/10. |
| `relacion_con_empresa` | `dueño` · `socio` · `empleado_operativo` · `consultor_externo` *(FunProtect: «dentro de la fundación yo soy docente, pero aparte soy su consultor»)* · `subordinado_delegado` *(Jenny: «A mí es subordinada»)* · `no_declarada` |
| `rol_en_decision` | `decide_solo` · `co_decide` · `recomienda_y_un_tercero_aprueba` · `evaluador_que_reporta_al_equipo` · `requiere_area_administrativa` · `desconocido` |
| `alfabetizacion_tecnica` | `alta_autonoma` *(FunProtect: «el tema no es ajeno a mi conocimiento», maestría en transformación digital)* · `media` · `baja_requiere_llave_en_mano` *(NūT: «te juro que tengo que estar horas para entender esto», dicho 3 veces)*. **Predice el paquete y la objeción dominante**, y en el corpus nunca se preguntó: se deduce de cómo pregunta el cliente. |
| `evidencia` | cita |

### `decisor`

`{ presente_en_demo: si|no|ambiguo, quien_decide, perfil_declarado, mecanismo:
solo|socios|junta_directiva|area_administrativa|equipo_evaluador, fecha_de_su_revision, evidencia }`

`presente_en_demo` es **enum de tres valores, no booleano**: en el corpus hay
5 sí, 4 no explícito y bloqueante, y varios ambiguos que nadie calificó. Cuando
es `no`, el patrón es idéntico y predecible: la llamada termina en «lo hablo con
X» sin fecha *(Jenny: «ella es la encargada de todo»; FunProtect: «el director
es abogado y mantiene con sus procesos penales»; American: «me siento con el
departamento administrativo»; Nicolás: «paso esta información al equipo»)*.
Cuando `presente_en_demo != si`, el prospecto **debe** traer una entrada en
`bloqueos_para_avanzar` y el diagnóstico se diseña para lectura autónoma
(misma regla que la ficha E1, campo `decisor_presente`).

### `stakeholders_ausentes[]`

`{ nombre, rol_previsto, por_que_importa, sera_usuario: bool }`. *(Megafoto:
Katia e Isamar, co-responsables del proyecto, nunca en la llamada; NūT: la
encargada de redes, que es quien hoy responde los DM y a quien el cambio le
toca el trabajo.)* Cada ausente es un carril del proceso que se diseñará sin su
dueño.

---

## B. `origen_y_detonante`

### `origen_lead`

`{ canal: bot_ia_ropofy | formulario_web_ropofy | facebook_organico |
facebook_ads_retargeting | referido | sdr_saliente | desconocido,
referidor: { nombre, relacion_con_ropofy }, sdr_previo, necesidades_predeclaradas[],
prebrief: { sector, n_asesores, dolor_declarado, validado_por_cliente: bool } }`

El pre-brief existe **antes** de la llamada en la mayoría del corpus (formulario
o conversación con el bot) y la ejecutiva lo recita al abrir. Registrarlo aparte
permite dos cosas: detectar que estaba mal (§A) y no volver a preguntar lo que
ya se validó. `referido` con `referidor` nombrado predice ausencia de objeciones
*(Dra Age: referida por Med Media, cero objeciones de precio, cerró sola)*.
`fuente_lead` quedó `desconocido` en 3/10 porque no se preguntó, o se preguntó
en el minuto 55 *(Droguería)*.

### `detonante[]` — el "por qué ahora"

`{ tipo, descripcion, tercero_involucrado, ventana_temporal, fecha_declarada,
es_fecha_dura: bool, evidencia }`

`tipo`: `contractual_con_tercero` *(American: convenio con Cámara de Comercio
que obliga aperturas)* · `afiliacion_a_cadena_o_franquicia` *(Droguería: 15-20
días para cambio de fachada)* · `apertura_de_canal_nuevo` · `saturacion_operativa`
*(Bifteki: «fines de semana son demasiados mensajes»; Megafoto: «se pierden
ventas por la capacidad de respuesta»)* · `restriccion_de_costo_de_personal`
*(American: «nos va a quedar muy difícil contratar este personal»)* ·
`encargo_de_un_decisor` *(FunProtect: «ingeniero, necesito captar estudiantes»)* ·
`hoja_de_ruta_previa_que_prescribe_la_compra` · `expansion_geografica` ·
`migracion_de_plataforma` *(Megafoto: salir de B2Chat)* ·
`evaluacion_de_proveedores_sin_fecha` *(Nicolás: «no tenemos fecha estimada de
salida de HubSpot»)* · `lanzamiento_de_marca` · `campanas_dejaron_de_rendir`.

**Distinción operativa:** un detonante con `es_fecha_dura: true` convierte el
next step sin fecha en un error caro, no en un detalle *(American tenía fecha
por convenio, disposición a acelerar y la llamada terminó en «cualquier duda por
WhatsApp»)*.

### `estado_de_compra`

| Campo | Notas |
|---|---|
| `competidores_en_evaluacion[]` | `{ nombre, estado: cotizado\|en_conversacion\|mencionado }`. *(Droguería llegó con pantallazo de 5 proveedores y «el viernes estuve con 23 personas indagando»; Nicolás: «estamos evaluando entre diferentes proveedores»; FunProtect comparaba lo que le llegaba por el mismo Facebook.)* **Es el campo con más señal comercial del schema y el guion no lo pregunta en ninguna parte.** |
| `n_procesos_paralelos` | Dato. |
| `plataforma_a_reemplazar` | `{ nombre, categoria, estado: activa\|contratada_sin_usar, motivo_salida, costo_actual, comparativo_de_costo }`. *(Megafoto: B2Chat activo con ~1.000 masivos, «cuándo nos podemos salir de Vituchat 2», motivo de salida `no_capturado / preguntado_sin_respuesta` — se preguntó y no se insistió; NūT: «Nubela», contratada sin implementar, a cancelar; Nicolás: HubSpot con 1.200 contactos.)* |
| `pidio_referencias` | bool + cita. *(Droguería: «me gustaría saber experiencias» — se prometieron y nunca se dieron en llamada.)* |
| `build_vs_buy` | `no_evaluado` · `resuelto_a_comprar` *(FunProtect: «si ya está hecho, ¿para qué va a complicar?»)* · `en_duda` · `construyendo_propio` *(Nicolás)*. |
| `desinformacion_previa[]` | `{ afirmacion, fuente_declarada, impacto }`. *(American: «me decían ayer en una reunión que al vincularla la podían bloquear»; Bifteki: otro proveedor le dijo que las plantillas tardan «de un día para el otro».)* El diagnóstico tiene que desmontarla, y para eso necesita saber que existe. |

---

## C. `negocio`

### `lineas_negocio[]`

Semilla directa del bloque A de la ficha (E1). Una entrada por línea de ingreso.
**No colapsar líneas que comparten canal** — misma trampa que en E1.

| Campo | Notas |
|---|---|
| `nombre` | |
| `tipo` | `b2c_minorista` · `b2b_mayorista` · `servicio_profesional` · `educacion_formacion` · `salud` · `intermediacion` · `retail_fisico` · `domicilios` |
| `modalidades[]` | `{ nombre: presencial\|online\|virtual\|domicilio\|salon, es_principal }`. *(American: «el fuerte de nosotros es el inglés presencial»; Bifteki: la misma comida para domicilio y para salón.)* |
| `es_principal` | bool |
| `politica_de_precio` | `publico` · `solo_en_entrevista` *(American: «para estos programas no se dan costos por teléfono, siempre se hace una entrevista»)* · `variable_por_certificacion` · `por_catalogo_mayorista` *(NūT)* · `volatil_por_inflacion` *(Bifteki: «la inflación mensual hace que cada tanto tengamos que subir los precios»)*. **Determina qué puede y qué no puede decir el bot** — es el insumo E4 más caro de descubrir tarde. |
| `paso_obligatorio_del_proceso` | `{ nombre, duracion_min, quien_lo_hace, es_virtualizable }`. *(American: entrevista de 15-20 min, hoy presencial, a virtualizar — define hasta dónde llega la IA.)* |
| `mecanismo_de_pago[]` | `contraentrega` *(Megafoto y Droguería: dominante)* · `transferencia` · `qr_o_tarjeta_en_entrega` · `anticipo_o_abono` *(Dra Age)* · `credito_propio` *(American: «cómo se genera un crédito», con requisitos de calificación)* · `pasarela` (0/10 la tenían para el canal comercial). |
| `insumo_requerido_del_cliente` | Qué debe entregar el comprador para que la venta avance. *(Megafoto: «si el cliente no nos ha enviado las imágenes, la venta no se puede terminar» — requisito funcional del bot: recibir archivos, no enviarlos.)* |
| `catalogo` | `{ estado: estructurado\|parcial\|en_construccion\|inexistente, donde_vive, items_activos, inventarios_separados }`. *(Droguería: 6 inventarios separados, «lo que no tiene una lo tiene la otra».)* |
| `ticket` / `ciclo_dias` / `recurrencia` | Dato. Ver §C.2. |

### C.2 `economia` — el bloque que el guion pide y la demo no produce

Checklist de datos duros, cada uno un `Dato`: `ticket_promedio`, `margen`,
`ad_spend_mensual`, `comision`, `tasa_de_cierre`, `facturacion`,
`presupuesto_declarado`, `costo_de_personal_sustituible`, `volumen_leads`.

**Hallazgo del corpus, y hay que diseñar con él, no contra él:**
ticket 0/10 · margen 0/10 · tasa de cierre 0/10 · ad spend con cifra 0/10 ·
presupuesto 0/10. `volumen_leads` aparece en ~5/10 y en 4 de esos casos el
número que se usó para cotizar **lo puso la ejecutiva**.

Por eso:

- **Ningún campo económico es obligatorio-con-valor.** Todos son
  obligatorio-con-`ausencia`. Un schema que exigiera valor sería violado por el
  100 % de las demos actuales, y eso no informa nada.
- `volumen_leads` es un objeto propio, no un número:
  `{ valor, unidad: leads|pedidos|conversaciones|mensajes, periodo: dia|turno|mes,
  tipo: actual|proyectado|historico, precision: medido|estimado_por_cliente|
  forzado_por_menu|supuesto_por_ejecutivo }`.
  *(Droguería: hoy 0 digitales y 50/día proyectados — dos diagnósticos opuestos
  en el mismo campo si no se separa `tipo`.)*
- `datos_economicos_capturados: { n, de: 9, modo_propuesta_previsto: "A"|"B" }`.
  Con la regla de E1: sin ticket, margen, comisión ni ad spend → **modo B**. En
  el corpus, **10/10 serían modo B**. Eso es un veredicto sobre el guion de la
  demo, no sobre los clientes.
- `benchmark_de_sustitucion` | Dato — cuando el cliente construye él mismo el
  ROI *(FunProtect: «pagar un asesor con prestaciones… digamos un millón al mes,
  se va a ahorrar mucha plata»)*. Es el único material económico que el corpus
  produce con fiabilidad, y viene del cliente sin que se lo pidan.

---

## D. `operacion_actual`

### `canales_entrada[]`

`{ canal, es_principal, volumen: Dato, quien_atiende, horario, evidencia }`

`canal`: `whatsapp` · `instagram_dm` · `facebook_msg` · `tiktok` · `email` ·
`formulario_landing` · `web_sin_formulario` *(FunProtect: «un landing que no
tiene ninguna funcionalidad, no hay cómo diligenciar un formulario»)* ·
`ecommerce` · `llamada_entrante` · `llamada_saliente` · `portal_sectorial` ·
`marketplace_delivery` · `asesores_en_campo` *(FunProtect)* ·
`mostrador_fisico` *(Droguería)* · `marca_franquiciante` · `boca_a_boca`
*(Astrid: «no hacemos campañas publicitarias» → «es por reconocimiento de la
empresa» → «Exactamente»)* · `base_propia`.

### `equipo_comercial`

`{ personas_que_atienden_leads: Dato, roles_mencionados[], horarios: Dato,
quien_responde_fuera_de_horario: Dato, terceros_que_operan_canales[] }`

`personas_que_atienden_leads` y `usuarios_solicitados` (§G) son **dos campos
distintos** y se confunden siempre *(Astrid: 5 comerciales, compró 3 usuarios)*.
El primero dimensiona el problema; el segundo, el precio. `terceros_que_operan_canales`
es material *(Dra Age: la agencia Med Media administra la pauta y necesitará
usuario de solo-vista; NūT: la community manager responde los DM desde Meta y el
cambio la afecta)*.

### `respuesta_y_seguimiento` — las cinco preguntas fijas

Un `Dato` por cada una, todas ⚑agenda:

1. `canales_de_entrada_confirmados`
2. `que_pasa_cuando_no_se_responde` + `frecuencia_de_no_respuesta`
3. `seguimiento_sistematizado`: `si` · `depende_de_que_alguien_se_acuerde` · `no_existe`
4. `medicion_de_leads_perdidos`: `automatica` · `manual` · `percepcion` · `no_puede`
5. `punto_de_quiebre_al_duplicar_volumen`

más `tiempo_de_respuesta_actual` y `exito_60_90_dias`.

**En el corpus estas preguntas se formularon 0 de 5 en 10 de 10 demos.** Los
dolores que sí aparecieron llegaron por iniciativa del cliente. Este bloque
existe, entonces, para dos cosas: registrar el vacío con su motivo (y por tanto
convertirlo en la columna vertebral de la agenda del diagnóstico) y alimentar la
métrica de indagación del §I. Si en algún momento el equipo empieza a
preguntarlas, este bloque se llena solo y la agenda se acorta.

### `stack[]`

`{ nombre, categoria, estado, es_fuente_de_verdad, api_disponible,
mecanismo_alternativo, debe_integrarse: obligatoria|deseable|no, riesgo, evidencia }`

`categoria`: `crm` · `erp_pos` · `software_vertical` · `ecommerce` ·
`pasarela_de_pago` · `bsp_whatsapp` · `agenda_calendario` · `email_marketing` ·
`sitio_web` · `perfil_google` · `hoja_de_calculo` · `plataforma_propia` · `telefonia`.

`estado`: `activo` · `activo_marginal` *(Jenny: «utilizamos poco los correos»)* ·
`parcialmente_automatizado` *(Astrid: respuestas básicas en WhatsApp)* ·
`contratado_sin_usar` *(NūT: Nubela)* · `en_construccion` *(Megafoto: web «en
construcción»; NūT: catálogo B2B)* · `deficiente_a_rehacer` *(NūT: «mi landing
mayorista está mal diseñada y mal armada»)* · `abandonado` *(Droguería: Google
My Business creado y sin uso)* · `a_cancelar` · `inexistente` ·
**`no_indagado`**.

`no_indagado ≠ inexistente`, y la diferencia es de diagnóstico, no de forma:
en *American* el CRM nunca se preguntó; en *Nicolás* había HubSpot con 1.200
contactos. Un extractor que colapse ambos casos en «no tiene CRM» produce una
ficha falsa.

**`api_disponible` + `mecanismo_alternativo`** existen por un caso que vale
citar entero: en *Droguería*, el cliente llamó en vivo a su proveedor de POS y
volvió con «todavía no manejan API, pero puede generar un CSV a un correo cada
30-60 minutos». Eso no es un detalle de integración: es la diferencia entre un
bot que vende stock real y uno que vende lo que no hay. `riesgo` guarda esa
consecuencia.

### `whatsapp`

| Campo | Notas |
|---|---|
| `n_lineas` | Dato. 1 a 3 en el corpus; «varias» sin cuantificar en 1 caso. |
| `tipo` | `personal_sim` · `business_app` · `api_verificada` · `api_en_bsp_tercero` *(Megafoto: la línea vive en B2Chat — migrar desde otro BSP nunca se abordó)* · `no_verificado` · `desconocido`. **`desconocido` o `no_verificado` en 8/10.** |
| `antiguedad_linea` | Dato. *(American: «es una línea que todo el mundo conoce durante más de 20 años, 23, 25 años».)* |
| `usos_actuales[]` | `chat` · `llamadas` · `campanas` · `estados` · `videollamadas`. Cada uso es algo que se pierde o se conserva al migrar a API. |
| `numeros_publicados[]` | Lo impreso en avisos y vitrinas no se apaga (regla heredada de E1). |
| `historial_bloqueo_meta` | `{ ocurrio: bool, motivo, cuando }`. *(Bifteki: «nos dieron de baja una por el tema de difusiones masivas» — y aun así no se corrió el filtro técnico.)* |
| `criticidad_de_la_linea` | `alta` · `media` · `baja`. Alta ⇒ la objeción de bloqueo va a aparecer; anticiparla es barato, improvisarla no. |
| `decision_del_numero_pendiente` | `mantener_en_app` · `migrar_a_api` · `numero_nuevo` · `unificar_lineas` · `pendiente`. Se resuelve en la sesión, no en la implementación. |
| `restricciones_aceptadas[]` | Lo que el cliente ya aceptó perder *(American: estados y videollamadas)*. Queda en acta. |

### `habilitacion_meta` — el bloque 12 del guion

`{ estado_del_filtro: completo|parcial|tardio|omitido,
business_manager: Dato, admin_del_bm: Dato, fanpage: Dato,
cuenta_publicitaria: Dato, bloqueos_o_restricciones: Dato,
categoria_permitida: Dato, accesos_en_manos_de_terceros: Dato }`

**Estado del filtro en el corpus: omitido 9/10, tardío y parcial 1/10.
Completo: 0/10.** Y se omitió precisamente en los casos de mayor riesgo: el
cliente que ya había perdido una línea por difusiones *(Bifteki)*, el que
tiene la pauta en manos de una agencia *(Dra Age)*, el que no tiene ni BM ni
fanpage ni cuenta publicitaria y planea «inundar las redes» *(Droguería)*, el
que trae una línea de 25 años desde otro BSP *(Megafoto, American)*.

Consecuencia de diseño: **el default de cada campo de este bloque es
`no_preguntado`, y cualquiera de ellos en ese estado hace `ruta_definida`
inelegible para `activacion_arquitectura` sin advertencia** (regla P5). No
porque el cliente no califique, sino porque nadie lo sabe.

---

## E. `dolores_y_requisitos`

### `dolores[]`

| Campo | Notas |
|---|---|
| `id` | slug |
| `enunciado` | En palabras del cliente cuando existan. |
| `arquetipo` | `arranque_de_canal_inexistente` · `fuga_por_saturacion` · `sin_seguimiento` · `sin_visibilidad` · `sin_precalificacion` · `dependencia_de_personas` · `costo_de_personal_para_escalar` · `dispersion_multicanal` · `inventario_o_catalogo_fragmentado` · `sobrecarga_cognitiva_del_dueño` · `fragilidad_del_canal` · `preguntas_repetitivas` · `sin_trazabilidad_de_origen` · `base_de_contactos_huerfana` |
| `quien_lo_verbalizo` | `cliente` · `ejecutivo` |
| `tipo` | `evidenciado` (pasa hoy y lo cuenta) · `anticipado` (lo temen a futuro) · `introducido_por_ejecutivo` (lo trajo la demo y el cliente no lo confirmó) |
| `cuantificado` | bool + `magnitud: Dato` |
| `citas[]` | `{ texto, hablante, minuto }` — mínimo una si `quien_lo_verbalizo == cliente` |

Dos hallazgos que el campo `arquetipo` existe para no perder:

**El guion asume un solo arquetipo y hay al menos dos.** `fuga_por_saturacion`
(*Megafoto*: 100+ mensajes/día y no alcanzan) y `arranque_de_canal_inexistente`
(*Droguería*: 0 leads digitales; *FunProtect*: «el marketing digital está
muerto») necesitan diagnósticos opuestos. Al segundo no se le puede preguntar
«¿cuántos leads pierden?»: no tiene leads que perder. El guion actual solo sabe
conversar con el primero.

**`cuantificado: false` en prácticamente todos los dolores del corpus.** Hubo
casos con el dato servido en bandeja —*Megafoto* dijo 100 mensajes/día y «se
pierden ventas por la capacidad de respuesta», y nunca se preguntó cuántas ni
cuánto vale una— y el precio quedó sin marco de ROI. Cuantificar el dolor es la
primera tarea del diagnóstico y este campo dice exactamente dónde empezar.

### `dolor_dominante_del_cliente`

El resumen que **el propio cliente** hace de lo que le importa, cuando lo hace.
Aparece espontáneamente y es el mejor dato de la llamada *(NūT: «a mí lo que me
importaba era el email marketing y las respuestas de WhatsApp a las consultas
B2B»; Jenny: «no sabemos qué persona está realmente interesada o quién pregunta
por curiosidad»; Droguería: «ustedes me pueden conectar al mundo digital y yo
puedo lograr ventas»)*. En varios casos la ejecutiva respondió «súper, listo» y
pasó a precio sin capitalizarlo.

### `requisitos_funcionales_declarados[]`

`{ requisito, tipo_de_componente_implicado, linea_de_negocio, cita }`

Aparece en 10/10 y no está en ningún campo del guion. Es insumo directo de E3/E4:
*Droguería*: buscar en 6 inventarios, notificar al domiciliario, escribir
siempre desde la línea principal · *Megafoto*: recibir imágenes del cliente y
perseguirlas hasta tenerlas · *American*: agendar la entrevista y nada más ·
*NūT*: campo personalizado "producto de interés" · *Bifteki*: resumen del pedido
para el telefonista, estadística de rendimiento humano, permisos por rol ·
*Nicolás*: flujos multicanal por stage.

### `alcance_ia_autorizado`

`precalifica_y_agenda_solamente` *(American, explícito: «lo más práctico es que
conlleven a la persona a la reunión y nosotros hacemos el resto»)* ·
`asesor_comercial_completo` · `atencion_y_faq` · `llamadas_salientes` ·
`no_definido`. Es la frontera que el cliente pone y que después se disputa.

### `restricciones`

`{ marca_blanca_requerida` *(FunProtect: «cuando yo hago mis campañas no salen
ustedes, solamente es la fundación»)*, `visibilidad_de_marca_limitada`
*(Droguería: zona con problemas de orden público, «entre menos lo conozcan a uno
mejor»)*, `propiedad_de_marca_en_tercero`, `confidencialidad_de_datos`
*(Jenny: clúster completo de almacenamiento, propiedad, respaldos y hackers)*,
`base_legal_de_contacto`, `otras[]` }`

---

## F. `reaccion_a_la_demo`

| Campo | Notas |
|---|---|
| `modulos_mostrados[]` | Enum cerrado y estable en el corpus: `conversaciones_omnicanal` · `agente_ia` · `bots_de_flujo` · `embudos_pipeline` · `seguimientos_automaticos` · `contactos_y_segmentos` · `campanas_masivas` · `email_marketing` · `calendario_agendamiento` · `cotizador` · `inventario_productos` · `marketing_planeador` · `ad_manager_reporteria_meta` · `dashboards` · `constructor_web` · `app_movil` · `permisos_y_roles`. |
| `modulos_con_interes_real[]` | `{ modulo, señal: n_preguntas\|cita\|tomo_notas\|interrumpio_para_pedirlo, evidencia }`. Interés declarado ≠ interés real: el proxy fiable es **cuántas preguntas hizo el cliente sobre ese módulo** *(Megafoto interrumpió: «¿el qué, el qué, pongo lo de marketing, ese me interesa»; Nicolás solo tomó notas en llamadas con IA)*. |
| `modulos_ignorados[]` | Los que se mostraron con detalle y no generaron ni una pregunta. Se repiten: dashboards, planeador de contenido, reportería Meta y email marketing consumieron minutos en casi todas las demos sin producir una sola pregunta. |
| `preguntas_del_cliente[]` | `{ texto, minuto, categoria, respondida: si\|no\|parcial\|prometio_averiguar }`. `categoria`: `funcional` · `comercial_precio` · `tecnica` · `confianza_y_datos` · `contrato_y_garantia` · `proveedor_subyacente` · `soporte_y_capacitacion` · `integraciones`. **Contar preguntas es el mejor medidor de engagement del corpus**: 10 en *Jenny*, 12 en *Nicolás*, 0 en *Astrid* (que igual dijo «está súper interesante»). |
| `preguntas_sin_responder[]` | Las que quedaron colgadas. *(Megafoto preguntó tres veces cuántos mensajes de WhatsApp puede enviar al día y nunca recibió la tarifa; Nicolás preguntó por integrar Dapta y recibió «déjame, yo le pregunto con el equipo», sin fecha.)* Cada una es deuda que el diagnóstico paga. |
| `senales_de_compra[]` | `{ texto, minuto, fuerza: alta\|media }`. *(Megafoto: «dile a Miguel qué hay que hacer, cuándo hacemos el primer pago»; American: «me gusta, prácticamente es lo que estoy buscando».)* |
| `senales_de_riesgo[]` | *(Astrid gestionó operación en vivo durante la demo; Jenny cortes de señal y cámara apagada; NūT dijo tres veces que no entendía.)* |
| `nivel_de_atencion` | `alta` · `media` · `interrumpida_por_operacion` · `degradada_por_fallas_tecnicas`. |

### `objeciones[]`

`{ tipo, cita, minuto, manejo, pendiente: bool }`

`tipo` — enum poblado enteramente por el corpus, sin inventar nada:
`precio_nivel` · `precio_claridad_de_estructura` *(Megafoto: «estoy enredado»,
por entrega goteada de 127 + 159 + implementación + WhatsApp; es distinta de
"caro" y se resuelve distinto)* · `precio_invertido` *(Droguería: «los costos
son muy bajitos» — señal de que el ancla quedó baja, no de buena noticia)* ·
`costo_variable_ia_o_whatsapp` *(la más frecuente y específica de Ropofy)* ·
`costos_ocultos` · `metodo_de_pago` *(Bifteki pidió transferencia; no existe)* ·
`sensibilidad_fx` *(American convirtió los 24 USD a pesos en voz alta)* ·
`autoridad_o_consenso` · `timing_o_presupuesto_futuro` ·
`competencia_en_evaluacion` · `prueba_social_faltante` ·
`bloqueo_de_linea_whatsapp` *(en 3 demos, siempre traída por el cliente, nunca
anticipada por Ropofy)* · `proveedor_subyacente` *(Nicolás: «¿ustedes están
montados en Go High Level?»)* · `integracion_con_terceros` ·
`seguridad_y_privacidad_de_datos` · `contrato_permanencia_garantia` ·
`complejidad_o_usabilidad` *(NūT)* · `capacidad_de_adopcion` ·
`duplicidad_con_stack_actual` *(NūT: «¿eso lo hago en Ropofy o en Tienda Nube?»)* ·
`riesgo_del_cambio_para_el_equipo` · `whitelabel_y_marca` ·
`legitimidad_del_proveedor` · `time_to_value` · `falta_de_criterio_propio`
*(American: «como no tenemos experiencia, no sabemos qué más vaya ahí»)* ·
`velocidad_invertida` *(Megafoto quería ir más rápido que Ropofy)* ·
`dilacion_sin_objecion`.

`manejo`: `resuelta` · `cliente_cede` · `minimizada_sin_trabajar`
*(NūT: el miedo a la complejidad se respondió con «es muy intuitiva», tres
veces, en vez de convertirlo en argumento de implementación llave en mano)* ·
`sembrada_por_el_ejecutivo` *(Jenny: la ejecutiva introdujo las cláusulas de
permanencia que el cliente no había preguntado)* · `sin_respuesta_prometio_averiguar` ·
`no_abordada`.

**`dilacion_sin_objecion` es el patrón de cierre real del corpus** y merece
nombre propio: el cliente no objeta nada, dice «mándame la propuesta y te
cuento», y la llamada muere sin fecha. Cero objeciones no significa avance.

---

## G. `lo_que_dijo_ropofy` — bloque de auditoría

Este bloque no describe al prospecto. Describe **lo que Ropofy prometió, dijo y
cotizó**, y existe porque en el corpus es simultáneamente el material más
abundante y el más inconsistente. No viaja a la ficha del cliente; viaja a
coaching y a control de catálogo.

### `cotizacion_dicha`

`{ plan_nombre, usuarios_cotizados, precio_plan_mes, modo_ia:
variable_por_conversacion|ilimitada, tarifa_ia_dicha, umbral_ia_dicho,
tarifa_whatsapp_dicha, pais_de_la_tarifa, implementacion_min_dicho,
implementacion_max_dicho, cotizacion_puntual_improvisada,
despegue_precio_dicho, despegue_dias_dicho, total_mensual_dicho,
supuesto_de_volumen_usado: { valor, origen }, minuto_del_primer_precio }`

Cotización completa en **10/10**, y en **10/10 antes del cierre #1**.

### `desviaciones_de_catalogo[]`

`{ concepto, valor_dicho, valor_de_catalogo, minuto, gravedad: alta|media|baja }`

Observadas en el corpus, con el catálogo diciendo **implementación desde USD 499**:
se dijo **300, 350, 399, 800** y rangos **399–2500** y **800–2500**. Además:
Despegue dicho como **14 días** y luego **15 días** en la misma llamada (2 casos);
umbral de IA ilimitada dicho como **700** y **800** en la misma frase (3 casos);
costo por email dicho como **0,001352** y luego **0,0025** (1 caso); tarifa de
WhatsApp confundiendo dólares y centavos (varios).

Este array es el que justifica el bloque entero: nadie lo habría visto sin un
registro estructurado por demo.

### `promesas[]`

`{ promesa, tipo: plazo|resultado|integracion|compatibilidad|entregable,
tiene_sustento: bool, riesgo, minuto, cita }`

*(«la implementación estaría en 3 a 4 semanas» sin conocer alcance; «Meta se
demora máximo 1 minuto» contradiciendo la política que se acababa de citar;
«mínimo crecen su tasa de conversión en un 30 %» sin fuente; «hemos aumentado
productividad hasta en un 30-40 %».)*

### `claims_sin_sustento[]` · `informacion_de_terceros_revelada[]`

El segundo existe por un caso concreto: en *Dra Age* se nombraron tres clientes
de Ropofy y se comentó la parametrización de uno de ellos delante de otro
prospecto. Es riesgo de confidencialidad y se registra.

### `entregables_prometidos[]`

`{ entregable, dueño, canal, fecha_comprometida, cumplido: bool|null }`

Recurrentes: propuesta/brochure, grabación, link de pago, referencias de
clientes, comparativo de ventajas y desventajas, costos de WhatsApp por país.
`fecha_comprometida` es `null` en la mayoría del corpus. Cada entregable sin
fecha es una promesa que el prospecto recuerda y Ropofy no.

---

## H. `cierres_y_resultado`

### `momentos_de_cierre`

Tres objetos —`cierre_1_valor_y_encaje`, `confirmacion_de_interes`,
`cierre_2_decision`— con la misma forma:

`{ ocurrio: bool, quien_lo_inicio: ejecutivo|cliente|no_ocurrio,
pregunta_formulada, hubo_silencio_despues: bool, respuesta_literal,
resultado: si|no|mas_o_menos|aplazado_a_tercero|no_se_pidio, minuto }`

`quien_lo_inicio` es el campo que más dice del corpus. En varias demos **el
cierre lo hizo el cliente**: *(Bifteki: «estaría bueno hacer un despegue»;
Dra Age: «entonces iniciamos con los 15 días de prueba, ¿no?»; Megafoto: «dile a
Miguel qué hay que hacer, cuándo hacemos el primer pago»; FunProtect: «sí quiero,
sí requiero, por favor»)*. Cuando el cliente cierra, la venta ocurre a pesar del
guion, no gracias a él — y eso no se puede ver sin registrarlo.

### `filtro_tecnico`

Espejo de `habilitacion_meta` (§D) desde la ejecución: `{ estado, minuto,
items_verificados[], items_omitidos[], derivo_a_atp: bool }`.

### `ruta_definida`

`activacion_arquitectura` · `atp_previo` · `no_fit_declarado` ·
`diferido_a_tercero` · `diferido_por_comparacion_de_proveedores` ·
`propuesta_prometida_sin_decision` · `sin_definir`.

`atp_previo` **se ofreció 0 veces en 10 demos**, incluyendo el caso sin BM, sin
fanpage y sin cuenta publicitaria. Es un producto que existe en el guion y no en
la práctica.

### `resultado_demo`

`pagado_en_llamada` · `link_enviado_pago_pendiente` · `link_prometido` ·
`propuesta_prometida_sin_fecha` · `decision_aplazada_a_tercero` ·
`diferido_por_competencia` · `perdido` · `sin_next_step`.

### `next_step`

`{ descripcion, tipo, dueño: ropofy|cliente|ambos, fecha, condicion,
tiene_fecha: bool }`

`tipo`: `cliente_escribira_por_whatsapp` · `cliente_paga_link` ·
`reunion_agendada_con_fecha` · `cliente_consulta_internamente` ·
`ropofy_envia_propuesta` · `ninguno`.

**`tiene_fecha: false` en 10/10.** El patrón fijo es «pagas → me confirmas por
WhatsApp → agendamos». Por eso `condicion` es un campo de primera clase: en este
proceso el disparador real casi nunca es una fecha, es un evento. Registrar la
condición en lugar de forzar una fecha inventada es lo honesto — y deja ver que
en los casos con detonante de fecha dura *(American, Droguería)* la falta de
fecha sí fue un error, no una característica del proceso.

### `temperatura_derivada`

`caliente` · `tibia` · `fria` · `no_evaluable`, con `criterios_aplicados[]`.
Derivada, nunca escrita a mano: se calcula de señales de compra, quién inició el
cierre, decisor presente, detonante con fecha dura y objeciones pendientes.

---

## I. `ejecucion_del_guion` — QA

### `bloques[]` — una entrada por bloque del guion auditado

`{ id, nombre, estado, minuto_inicio, micro_checks_obligatorios:
[{ check, ocurrio }], notas }`

El conjunto de `id` debe coincidir exactamente con el mapa canónico de la
`version_guion` declarada (P13): **v2026 / v3** → 13 bloques, ids `1..13`;
**v4.1** → 19 bloques, ids `0, 1.1, 1.2, 1.3, 1.4, 1.5, 2, 3, 4, 5, 6, 7, 8,
9, 10, 11, FT, 12, 13` (las situaciones especiales del v4.1 no son bloques:
se auditan vía `objeciones[].manejo` y `errores_detectados[]`). En v4.1 los
ids `3` (recap) y `4` (transición) conservan la semántica de validación y
encuadre que el QA puntúa.

`estado`: `ejecutado` · `ejecutado_debil` · `parcial` · `omitido` ·
`fuera_de_orden` · `iniciado_por_el_cliente`.

Línea base del corpus (n=10), para que cualquier medición futura tenga contra
qué compararse:

| Bloque | Estado dominante |
|---|---|
| 1 Apertura y encuadre | ejecutado (breve) — el mejor cumplido |
| 2 Descubrimiento | parcial en todos; **0/5 preguntas fijas en 10/10** |
| 3 Validación del entendimiento | **omitido en 10/10** |
| 4 Encuadre del demo | **omitido en 10/10** — la pantalla se comparte sin encuadre |
| 5 Demo conversacional | ejecutado, pero como tour de features; monólogos de 6-15 min |
| 6 Cierre #1 | omitido o `ejecutado_debil` («¿tienes alguna pregunta?») |
| 7 Confirmación de interés | omitido; la señal llegó espontánea del cliente |
| 8 Camino 1-2-3 | parcial y fuera de orden (después del precio) |
| 9 Paso 1 Arquitectura/Despegue | ejecutado, con inconsistencias 14/15 días |
| 10 Paso 2 Implementación | ejecutado, con desviación de precio frecuente |
| 11 Cierre #2 | **omitido en 10/10**; cuando hubo decisión, la trajo el cliente |
| 12 Filtro técnico | omitido 9/10, tardío y parcial 1/10 |
| 13 ATP / Activación | ATP **0/10**; activación parcial (link prometido) |

### `preguntas_fijas_descubrimiento[]`

Cinco entradas: `{ n, enunciado_canonico, formulada: si|no|parcial|reformulada_como_configuracion,
respuesta_obtenida, minuto }`.

`reformulada_como_configuracion` es un valor necesario, no un matiz: en el
corpus las preguntas de descubrimiento se sustituyeron sistemáticamente por
preguntas para poder cotizar («¿cuántas líneas tienen?», «¿cuántos usuarios?»,
«¿manejan CRM?»). Se parecen a descubrimiento y no lo son: sirven al precio, no
al diagnóstico.

### `metricas_ejecucion`

`{ duracion_efectiva_min, minuto_pantalla_compartida, minuto_primer_precio,
monologo_mas_largo_min, n_preguntas_del_ejecutivo, n_preguntas_del_cliente,
n_checkpoints_en_demo, adherencia_bloques: "n/13",
preguntas_fijas_formuladas: "n/5", dolores_cuantificados: "n/m" }`

`minuto_primer_precio / duracion_efectiva` es la métrica más diagnóstica del
corpus: precio en el minuto 8 de 42, en el 11 de 17, en el 12 de 14, en el 20 de
38. El precio llegó antes del valor casi siempre, y casi siempre porque el
cliente lo pidió y nadie lo aplazó — que es exactamente la variante que el guion
prevé en el bloque 1 y nadie usó.

### `errores_detectados[]`

`{ codigo, minuto, cita, gravedad }`. Enum derivado del corpus:
`descubrimiento_omitido_o_minimo` · `preguntas_apiladas` ·
`pregunta_de_configuracion_en_lugar_de_dolor` · `demo_sin_encuadre` ·
`monologo_prolongado_sin_checkpoint` · `demo_conducida_por_el_cliente` ·
`modulos_irrelevantes_mostrados` · `pantalla_rota_o_dashboards_vacios` ·
`fallo_tecnico_en_vivo` · `precio_antes_de_cierre_1` ·
`precio_inconsistente_con_catalogo` · `inconsistencia_interna_de_precio` ·
`cotizacion_sobre_volumen_supuesto` · `descuento_o_downgrade_no_solicitado` ·
`dolor_no_cuantificado` · `sin_validacion_del_entendimiento` ·
`avance_sin_validacion_explicita` · `autoridad_no_calificada` ·
`identidad_del_interlocutor_no_confirmada` · `cargos_y_stakeholders_no_capturados` ·
`filtro_tecnico_omitido` · `atp_no_ofrecido` · `objecion_minimizada` ·
`objecion_sembrada_por_el_ejecutivo` · `pregunta_del_cliente_sin_responder` ·
`respuesta_tecnica_insegura` · `claim_sin_sustento` ·
`promesa_de_plazo_sin_alcance` · `informacion_de_terceros_revelada` ·
`jerga_no_entendida_no_aclarada` · `cierre_pasivo_sin_pedir_decision` ·
`next_step_sin_fecha` · `senal_de_compra_no_capitalizada` ·
`grabacion_dejada_corriendo`.

---

## J. `calidad_y_agenda` — el output que consume la Etapa 1

### `datos_en_conflicto[]`

`{ tema, objeto_a, version_a, objeto_b, version_b, impacto, estado }`

`estado`: `abierto` · `resuelto_a_favor_del_cliente` · `resuelto_a_favor_del_registro_previo` · `sin_resolver_requiere_tercero`.

Misma regla dura que E1: **antes de declarar conflicto, verificar que las dos
versiones hablan del mismo objeto.** Si difieren, no hay conflicto: son dos
datos ciertos y ambos se registran. En este corpus el patrón típico es cliente
vs. formulario (vertical, empresa) y ejecutivo vs. ejecutivo (los umbrales 700 /
800 en la misma frase).

### `hipotesis_a_verificar[]`

`{ afirmacion, quien_la_introdujo, por_que_es_hipotesis, como_verificarla,
riesgo_si_es_falsa }`

Se puebla automáticamente con todo dato cuya `fuente` sea
`ejecutivo_afirmo_sin_confirmar`, `ejecutivo_supuso_para_cotizar`,
`cliente_asintio` o `cliente_forzado_por_menu`, y con toda inferencia material
del extractor (las `inferido_de_transcripcion` que cambien una decisión; las
demás basta con que declaren su `nota_de_inferencia`).
Es la lista de lo que la demo *cree* saber. Ejemplos del corpus: los 500
leads/mes de *FunProtect* (inventados), el estatus de API verificada de
*Nicolás* (nunca comprobado), el perfil entero de *Astrid* (construido sobre
«Mhm»).

### `vacios[]`

`{ campo, motivo, impacto: bloquea_propuesta|encarece_diagnostico|informativo }`

Derivado de todos los `Dato` con `ausencia != null`. Es la lista literal de
huecos, y su tamaño esperado tras una demo real de 30-45 minutos es **de 15 a
30 entradas**. Un prospecto con 3 vacíos no es una demo excelente: es una
extracción que inventó.

### `agenda_diagnostico[]` — la razón de ser del archivo

`{ id, pregunta_sugerida, campo_destino: <ruta en ficha.json>, por_que_importa,
quien_debe_responder: <función>, prioridad: bloqueante|alta|media,
momento: brief_previo|en_sesion|evidencia_en_vivo,
requiere_dato_previo, deriva_de: <id de vacío/hipótesis/conflicto> }`

Reglas de construcción:

**J1 — Toda entrada deriva de algo.** `deriva_de` es obligatorio y apunta a un
`vacio`, una `hipotesis_a_verificar`, un `dato_en_conflicto`, una
`pregunta_sin_responder` o un `requisito_funcional_declarado`. Ninguna pregunta
se agrega "porque suele preguntarse": para eso ya existe el guion base del
diagnóstico. Esta agenda es **el delta de este cliente**.

**J2 — Nada que ya se sepa entra a la agenda.** Si el dato existe con `fuente`
`cliente_declaro` o `cliente_confirmo`, no se pregunta: se confirma, y eso lo
hace el renderizador del guion, no esta lista.

**J3 — El momento se asigna por naturaleza del dato, no por importancia.**
Hechos que el cliente puede responder solo → `brief_previo` (razón social,
sedes, horarios, oferta, modismos). Lógica, decisiones y números que exigen
conversación → `en_sesion`. Cuentas, líneas, dominios, inventarios y bloqueos →
`evidencia_en_vivo`: **se ven en pantalla, no se preguntan de memoria** (regla
E2 de la etapa 4). Todo el bloque `habilitacion_meta` es `evidencia_en_vivo` por
definición.

**J4 — Prioridad `bloqueante` solo si impide construir la propuesta.** En el
corpus, los bloqueantes reales son tres y se repiten: habilitación Meta sin
verificar, decisor ausente sin fecha de su revisión, y ausencia total de datos
económicos (que fuerza modo B y por tanto cambia la forma de la propuesta, no
solo su contenido).

**J5 — Un dolor sin cuantificar genera pregunta de cuantificación, siempre.**
Con la magnitud del negocio, no con la del sector: «dijiste que se pierden
ventas por no alcanzar a responder; de esos 100 mensajes al día, ¿cuántos se
quedan sin respuesta y cuánto vale uno que se cierra?».

**J6 — El arquetipo del dolor decide el eje de las preguntas.** Con
`arranque_de_canal_inexistente` no se pregunta por fugas: se pregunta por la
construcción del canal y por el punto de partida contra el cual se medirá.
Preguntarle a *Droguería* cuántos leads pierde es preguntarle por algo que no
tiene.

### `bloqueos_para_avanzar[]`

`{ bloqueo, tipo: tecnico|comercial|legal|dependencia_externa, dueño, consecuencia }`

Obligatorio (reglas P5 y P6) cuando la habilitación Meta está sin verificar o
cuando el decisor no estuvo en la demo. No es una lista de excusas: es lo que
el consultor tiene que resolver **antes** de que la propuesta signifique algo.

### Campos derivados de cierre

`modo_propuesta_previsto: A|B` · `bloqueos_para_avanzar[]` ·
`resumen_para_el_consultor` (≤ 10 líneas, en prosa, para el humano que abre el
diagnóstico) · `score_de_ejecucion: { adherencia_bloques, preguntas_fijas,
indagacion_economica, errores_graves }`.

---

## 4. Reglas duras de extracción

**R1 — Nunca inferir.** Dato dicho → se registra con evidencia. Dato no dicho →
`no_capturado` con su `ausencia`. Jamás se completa con lo típico del sector, ni
con la plantilla de demo de esa vertical, ni con lo que "seguramente" aplica.
Heredada de E1 y no negociable.

**R2 — Quien lo dijo importa más que qué se dijo.** Antes de registrar cualquier
número, resolver si lo dijo el cliente, lo dijo la ejecutiva, o lo eligió el
cliente de un menú de la ejecutiva. Los tres casos son datos distintos.

**R3 — Toda cifra lleva unidad y periodo.** «100» no es un dato. «100
mensajes/día, actual, declarado por el cliente» sí.

**R4 — Números corregidos en la misma sesión: vale el último, y la evidencia
cita ese.** La gente redondea y luego precisa.

**R5 — Distinguir volumen actual de proyectado.** Son diagnósticos opuestos y
en el corpus se mezclaron.

**R6 — El audio ambiente es contexto, nunca cita ante el cliente.** Se registra
con `fuente: audio_ambiente` y no se usa para confrontar a nadie.

**R7 — Cero recomendaciones, cero componentes, cero precios propuestos.** Esta
etapa registra. El diagnóstico evalúa; E3 propone. Un `prospecto.json` con
componentes sugeridos está mal hecho.

**R8 — Lo que Ropofy prometió se registra con el mismo rigor que lo que el
cliente dijo.** El bloque G no es opcional ni cortés: las promesas de plazo y
las desviaciones de precio son obligaciones que el diagnóstico hereda.

---

## 5. Validaciones (`validar_prospecto.py`)

| # | Regla | Efecto |
|---|---|---|
| **P1** | `valor == "no_capturado"` ⟺ `ausencia != null` | error |
| **P2** | Todo `Dato` tiene `fuente`; si `fuente` es `cliente_*` o `ejecutivo_*`, tiene `hablante` | error |
| **P3** | Todo dato con valor no obvio tiene `evidencia`; toda `evidencia` usa «» y ≤ 200 caracteres | error |
| **P4** | Todo `no_preguntado` en campo ⚑agenda aparece en `vacios[]` y genera entrada en `agenda_diagnostico[]` con `deriva_de` | error |
| **P5** | Si algún campo de `habilitacion_meta` es `no_preguntado`, `ruta_definida` no puede ser `activacion_arquitectura` sin una entrada en `bloqueos_para_avanzar` | error |
| **P6** | Si `decisor.presente_en_demo != "si"`, existe entrada en `bloqueos_para_avanzar` | error |
| **P7** | Todo dato con `fuente` en {`ejecutivo_supuso_para_cotizar`, `ejecutivo_afirmo_sin_confirmar`, `cliente_asintio`, `cliente_forzado_por_menu`} aparece en `hipotesis_a_verificar[]`; si la cotización usó un volumen supuesto, también | error |
| **P7b** | Todo dato con `fuente: inferido_de_transcripcion` declara `nota_de_inferencia`; `cliente_forzado_por_menu` obliga `confianza: baja` | error |
| **P8** | `datos_economicos_capturados.modo_propuesta_previsto == "B"` si faltan ticket, margen, comisión y ad spend | error |
| **P9** | Toda cifra numérica tiene `unidad`; `volumen_leads` tiene `tipo` y `precision` | error |
| **P10** | `datos_en_conflicto[]`: solo si `objeto_a == objeto_b` | error |
| **P11** | Todo `dolor` con `quien_lo_verbalizo == "cliente"` tiene ≥ 1 cita | error |
| **P12** | Todo `dolor` con `cuantificado == false` genera entrada en `agenda_diagnostico` (regla J5) | error |
| **P13** | El conjunto de ids de `bloques[]` coincide con el mapa canónico de la `version_guion` declarada (13 para v2026/v3; 19 para v4.1); `preguntas_fijas_descubrimiento[]` exactamente 5 | error |
| **P14** | Cotización dicha vs. catálogo: toda diferencia queda en `desviaciones_de_catalogo[]` | error |
| **P15** | `agenda_diagnostico[]`: `deriva_de` resuelve a un id existente; `campo_destino` apunta a una ruta válida de ficha.json | error |
| **P16** | Ninguna entrada de `agenda_diagnostico` pregunta por un campo que ya tiene valor con `fuente` `cliente_declaro` o `cliente_confirmo` (regla J2) | **advertencia** mientras `campo_destino` apunte a rutas de ficha.json que el validador no puede resolver; pasa a error cuando exista el mapeo formal (§6) |
| **P17** | Todo bloque de `habilitacion_meta` en `agenda_diagnostico` tiene `momento: evidencia_en_vivo` (regla J3) | error |
| **P18** | El JSON parsea; `_meta` completo; `version_schema` presente | error |
| **A1** | `vacios[]` con menos de 8 entradas en una demo > 20 min | **advertencia**: probable invención |
| **A2** | `dolores[]` sin ninguna cita textual | advertencia |
| **A3** | `next_step.tiene_fecha == false` con `detonante.es_fecha_dura == true` | advertencia: error comercial, no de extracción |
| **A4** | `preguntas_del_cliente[]` vacío en demo > 15 min | advertencia: revisar si se perdió engagement o la extracción |

---

## 6. Pendientes v0.1

- **Calibrar contra una demo bien ejecutada.** Las 10 fuentes comparten
  ejecutivo y patrón de ejecución (mismos 4 bloques ausentes en todas). El
  schema puede estar sobreajustado a *esta* forma de fallar. Una demo con
  descubrimiento completo y filtro técnico corrido diría si los campos de §D
  y §I aguantan el caso bueno.
- **Mapa formal `prospecto.json` → `ficha.json`.** Cada campo de aquí debería
  declarar su `campo_destino` en el contrato de E1, para que la semilla se
  aplique automáticamente y `agenda_diagnostico` se derive sin criterio humano.
  Hoy el mapeo vive solo en `agenda_diagnostico[].campo_destino`, entrada por
  entrada.
- **Banco de preguntas por vacío.** `agenda_diagnostico[].pregunta_sugerida` se
  redacta hoy caso por caso. Debería salir de una tabla vacío → pregunta
  canónica (con el default de metodología que exige la regla E1 de la etapa 4:
  proponer-primero, nunca preguntar en blanco).
- **Tarifas y precios de catálogo como archivo versionado.** `desviaciones_de_catalogo`
  compara hoy contra valores incrustados en el validador. Deberían vivir en un
  `catalogo-precios.json` con fecha de vigencia; parte de las "desviaciones"
  observadas pueden ser cambios de lista que el guion no recogió.
- **Umbral de temperatura.** `temperatura_derivada` necesita su fórmula
  explícita y calibración contra resultado real (quién pagó) antes de que
  alguien la use para priorizar pipeline.
- **Verticales del guion.** El Excel trae hojas por vertical (concesionarios,
  clínicas, inmobiliarias, educación, B2B) con insights y preguntas propias.
  `modulos_mostrados` y `dolores[].arquetipo` deberían poder resolverse contra
  la hoja de la vertical del prospecto, y hoy no hay campo que declare qué hoja
  se usó ni si era la correcta.
