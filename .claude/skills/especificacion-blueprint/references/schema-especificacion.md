# Schema `especificacion_requerida` — Etapa 4: de propuesta aceptada a blueprint

Contrato de datos v0.2. Extiende el schema de componente v0.2.
Caso de calibración: sesión Kombat Motos, 12-ago-2026 (72 min, sin guion) —
se cita como *(Kombat)* donde una decisión de diseño sale de esa evidencia.
v0.2 (19-ago-2026) incorpora el Excel de levantamiento "Promt BOT IA" y las
guías de identidad del agente — material de campo que validó la estructura
del guion y aportó el momento `brief_previo`, los parámetros de conversación
y los cierres canónicos. Se cita como *(Excel)*.

**Posición en la cadena:** ficha.json (E1) → diagnostico.json (E2) →
propuesta.json (E3) → **sesión de especificación (E4)** → `blueprint.json`.
La etapa 4 no descubre alcance: lo **especifica**. El alcance quedó congelado
en propuesta.json; lo que no quepa en un campo de este schema es change request.

---

## 0. Dónde vive el bloque y sobre qué corre

- `especificacion_requerida` se define a nivel de **`tipo`** (los 17 tipos del
  schema v0.2 ya determinan qué campos del `detalle` hay que llenar). Un
  componente puede añadir ítems propios en `especificacion_extra`, nunca
  quitar los del tipo.
- La especificación corre por **instancia**, no por componente. El pipeline de
  KTM y el de Auteco son dos juegos de respuestas *(Kombat: alta y baja gama
  con Impulsa separados, saludo distinto por marca)*. Cada ítem declara
  `hereda_entre_instancias` para no repetir 10 veces lo que se responde una vez.
- El guion de la sesión **se genera** desde propuesta.json: componentes
  seleccionados × instancias × ítems de especificación, ordenados por
  `posicion_journey`. Nadie improvisa el orden.

**Producto de la etapa:** `blueprint.json` =
propuesta.json instanciado + `detalle` de cada instancia lleno +
`guia_de_voz` (§2) + `checklist_habilitacion` resuelta o con dueños +
acta de alcance firmable (vista de cliente del mismo JSON).

---

## 1. Schema del ítem de especificación

| Campo | Tipo | Notas |
|---|---|---|
| `id_item` | slug | Estable. El blueprint guarda respuesta por `id_item` × instancia. |
| `campo_destino` | ruta | Apunta a un campo del `detalle` del tipo (ej. `detalle.variables[]`). **Toda respuesta aterriza en un campo**; una pregunta sin campo destino no existe. |
| `pregunta_guion` | texto | Redactada en lenguaje del cliente, lista para leerse en voz alta. |
| `quien_responde` | funcion | De la taxonomía de funciones de la ficha. *(Kombat: Rafa responde taller y canales; Cristian responde pauta y comercial — sin rol, la sesión le pregunta scoring al que no opera el embudo.)* |
| `tipo_respuesta` | enum | `seleccion` · `texto` · `numero` · `inventario_verificado` · `decision_arquitectura` · `aprobacion_copy` |
| `default_metodologia` | valor | **Obligatorio salvo en `inventario_verificado`.** La respuesta recomendada por Ropofy, pre-cargada. El guion propone y el cliente ajusta — nunca pregunta en blanco. *(Kombat: "ustedes son los expertos… nosotros proponemos y tú aceptas si es lo que quieres".)* |
| `consecuencias` | [texto] | **Obligatorio si `decision_arquitectura`.** Trade-offs pre-redactados que el consultor lee antes de que el cliente decida. *(Kombat: API vs. 5 líneas Business — bloqueo de línea por volumen, plantillas tras 24 h, formularios. La explicación existió porque Jaime la sabía; el schema la vuelve del sistema.)* |
| `momento` | enum | `brief_previo` · `en_sesion` · `asincrono_cliente` · `checklist_habilitacion`. Ver §3. |
| `hereda_entre_instancias` | bool | true = se responde una vez y aplica a todas las instancias del componente; false = se pregunta por instancia. |
| `evidencia_en_vivo` | texto? | Si existe, la respuesta no se acepta de memoria: se verifica compartiendo pantalla (cuenta conectada, anuncio corriendo, campo existente). *(Kombat: 10 min para desenredar 4 cuentas Meta y 2 códigos Impulsa; "combat usadas" apareció conectada pero excluida — eso solo se ve en vivo.)* |
| `calculo_roi` | objeto? | `{ formula, insumos[] }`. Para componentes con `costo_externo: consumo_variable`: la cuenta se hace en sesión con los números del cliente. *(Kombat: TransUnion, ~800 consultas × $700 vs. horas de asesor — el cierre de la objeción fue la aritmética en vivo.)* |
| `obligatorio` | bool | Un ítem obligatorio sin respuesta bloquea el cierre del blueprint (regla S1). |

### Notas de diseño

**Proponer-primero no es estilo, es rendimiento.** La pregunta abierta produce
al cliente diseñando en vivo *(Kombat: Rafa proponiendo su propio flujo hecho
"ayer" que "cambió toda la operación")*. El default de metodología convierte
cada ítem en una confirmación de 30 segundos o una corrección con dirección.

**`decision_arquitectura` es una clase aparte** porque su costo de error es
estructural, no cosmético: canal (API vs. Business), instanciación (¿un flujo
por marca o trigger por anuncio?), qué cuentas entran y cuáles no. Siempre
lleva `consecuencias`, siempre `momento: en_sesion`, nunca hereda silenciosa.

**Lo que el cliente ya respondió no se vuelve a preguntar.** Si el dato vive
en ficha.json o diagnostico.json, el ítem lo trae pre-llenado con fuente y el
guion solo lo confirma. Preguntar dos veces erosiona la autoridad del proceso.

---

## 2. Activo transversal: `guia_de_voz`

La voz **no es propiedad de ningún componente**. Se especifica una vez por
cliente, se versiona, y todo componente con copy (`mecanismo_entrega:
contenido_a_medida`, `plantilla_mensaje`, `chatbot_ia`) la hereda.

*(Kombat: dos años sin este activo produjo tres personalidades de bot —
"Óscar" que hablaba de más, uno intermedio que cerraba, y el actual que
"parece pegado" y responde ambiguo. El cliente lo percibe como producto
inestable; era ausencia de spec.)*

```
guia_de_voz:
  version, fecha, aprobada_por          # se versiona: el drift se detecta contra esto
  identidad_asistente:
    nombre                              # el bot tiene UN nombre estable
    genero                              # (Excel) coherente con el nombre; lo elige el cliente
    se_declara_asistente: bool          # ¿dice que es un asistente virtual?
    de_parte_de                         # "Te hablamos de Motos Combat…"
  tratamiento: tu | usted | segun_perfil | espeja_al_cliente   # (Excel: adaptarse a cómo abre el cliente)
  tono: texto corto + 3 ejemplos reales del cliente
  lexico_propio[]                       # cómo llaman ellos a sus cosas (Excel: modismos permitidos)
  palabras_prohibidas[]
  emojis: nunca | moderado | libre
  usa_nombre_contacto: bool             # (Excel) llamar al cliente por su nombre — recomendado solo
                                        # si el dato entra por formulario o se confirma; con nombres
                                        # sucios o alto volumen orgánico es contraproducente
  parametros_conversacion:              # (Excel · config técnica — hereda a todo chatbot_ia)
    max_lineas_por_respuesta            # inmediatez: nadie lee párrafos en WhatsApp
    interpreta_notas_de_voz: bool       # transcripción con margen de error declarado
    interpreta_imagenes: bool           # entra en contexto; nunca diagnostica ni concluye
    idiomas: { principal, adicionales[] }
  saludo_base
  variantes_por_punto_de_ingreso[]:     # la ÚNICA parte de voz que varía por origen
    { origen, que_contexto_declara, que_verifica }
    # (Kombat: "debes tener un saludo diferente para cada punto de ingreso" —
    #  el lead de Impulsa llega frío y el saludo re-verifica el vehículo;
    #  el de WhatsApp directo no sabe qué moto quiere; el de formulario ya respondió.)
  cierres_canonicos:                    # (Excel) los 4 finales de toda conversación — se aprueban
    transferencia_en_horario            #   como copy, una vez, y todo componente los hereda
    transferencia_fuera_de_horario      #   (declara horario y compromiso de retorno)
    descarte                            #   la salida digna: agradece, explica, deja la puerta abierta
    inactividad                         #   cierre por no-respuesta, con invitación a retomar
  manejo_de:
    insulto_o_agresion                  # (Kombat: "vales mondá" — pasó, y no había regla)
    silencio, fuera_de_horario, fuera_de_alcance, solicitud_de_humano
    cliente_indeciso                    # (Excel) ¿redunda sin definir? → escalar o cerrar, se decide aquí
    cliente_molesto_o_reclamo           # (Excel) ruta de reclamación, siempre con opción humana
```

Las **reglas universales del asistente** (no inventar, no prometer precios
finales, no mencionar sistemas internos, una pregunta a la vez, no salir del
rol) no se especifican por cliente: son defaults duros del catálogo de
habilidades (§0 del catálogo) y el guion solo las informa.

Regla dura: **ningún copy se activa sin `guia_de_voz` aprobada** (S5). El
texto final lo aprueba el cliente (regla global del copy, schema v0.2 §1),
pero lo aprueba **contra** esta guía, en asíncrono — redactar saludos en vivo
es el uso más caro posible de la sesión.

---

## 3. Los tres momentos

| Momento | Qué se resuelve | Regla |
|---|---|---|
| `brief_previo` | Hechos que el cliente puede responder solo, sin consultor: identidad del negocio, oferta por sede, horarios de atención humana, mercado objetivo, sitios web, nombre y género del asistente, modismos y palabras prohibidas. *(Excel: la columna "Momento en el que se define = Brief" ya operaba así.)* | Se envía **al aceptar la propuesta**, junto con el checklist. Solo preguntas de hecho — **jamás** una `decision_arquitectura` ni un `inventario_verificado`. La sesión abre validando el brief, no repitiéndolo. |
| `en_sesion` | Lógica y decisiones: qué dispara qué, qué se pregunta, dónde corta, quién recibe, con qué consecuencia. | Todo `decision_arquitectura` y todo `inventario_verificado` viven aquí. |
| `asincrono_cliente` | Copy y material: aprobación de plantillas redactadas por Ropofy desde la guía de voz, entrega de piezas, fotos, catálogo. | Sale de la sesión con fecha y dueño. Al cliente le cuesta menos corregir que crear. |
| `checklist_habilitacion` | Credenciales, WhatsApp API, accesos Meta/CRM, dominios a reapuntar, dueño técnico del lado del cliente. | **Arranca el día de la aceptación de la propuesta, no espera la sesión.** Es lo que más proyectos frena y no depende de nadie pensando. *(Kombat: dominio combatmotos.com muerto en toda la pauta — dos años sin que nadie lo tuviera en una lista.)* |

---

## 4. Bloques por tipo

Formato compacto: **campo destino ← pregunta (default) [momento]**. Los ítems
marcados ⚑ son `decision_arquitectura`. Salvo nota, `quien_responde` es el
dueño del proceso que el componente automatiza y `hereda_entre_instancias: false`.

### `pipeline`
- `etapas[]` ← "Recorramos el camino de un cliente desde que escribe hasta que compra: ¿qué hitos marcan el paso de una etapa a otra?" (default: etapas de la librería para su vertical) [en_sesion]
- `etapas[].sla_dias` ← "¿Cuánto puede quedarse un cliente en esta etapa antes de que alguien deba enterarse?" (default por etapa) [en_sesion]
- `motivos_perdida[]` ← "Cuando hoy pierden un cliente, ¿cuáles son las 4–5 razones reales?" (default del vertical; *Kombat: "reportado" es motivo de pérdida estructural, no un texto libre*) [en_sesion]
- ⚑ `se_instancia_por` (confirmación) ← "¿Este embudo es uno solo o uno por marca/línea?" (consecuencias: reporteo separado, doble mantenimiento; *Kombat: KTM vs. Auteco, y dentro de Auteco alta/baja gama*) [en_sesion]

### `campos_personalizados` / `objeto_personalizado`
- `campos[]` ← se presenta el set default del vertical y se pregunta solo "¿qué decisión toman ustedes que estos campos no capturan?" (default: librería) [en_sesion]
- `campos[].unico` ← lo decide Ropofy, no se pregunta — es irreversible; el guion solo lo informa. [en_sesion]

### `automatizacion`
- `disparador` ← "¿Qué evento exacto enciende esto?" con el inventario de puntos de entrada delante (default: librería) [en_sesion]
- `ramas[]` ← "Si el cliente responde X, ¿qué pasa? ¿Y si no responde en N horas?" (default: árbol de la librería) [en_sesion]
- `acciones[].asigna_a_funcion` ← "¿A quién de su equipo le cae esto?" — contra el mapa de roles de la ficha (*Kombat: Rafa taller / Cristian comercial*) [en_sesion]
- Regla de descarte con salida digna: toda rama que descarta un lead define **mensaje de salida** y **a quién NO le llega**. *(Kombat: reportado → "en este momento no podemos gestionar tu crédito… estamos atentos" y el asesor nunca lo ve. Son dos mecanismos: autofiltro declarado y filtro del sistema — se especifican ambos.)* [en_sesion]

### `plantilla_mensaje`
- `proposito`, `variables[]` ← en sesión solo se confirma qué información lleva cada mensaje. [en_sesion]
- Texto final ← Ropofy redacta desde `guia_de_voz`; cliente aprueba. `tipo_respuesta: aprobacion_copy` [asincrono_cliente]
- `requiere_aprobacion_meta` ← no se pregunta; se deriva y se informa el plazo. [checklist_habilitacion]

### `formulario` / `encuesta`
- `campos[]` ← "¿Qué necesita saber su equipo ANTES de hablar con el cliente, y qué pregunta sobra porque genera fricción?" (default: 3 preguntas de triage del vertical; *Kombat: forma de pago, cuándo compra, modelo de interés — la tercera la aportó la metodología, no el cliente*) [en_sesion]

### `calendario`
- `modalidad`, `asignacion_por` ⚑ ← "¿Las citas caen a una persona, rotan entre el equipo, o dependen de la sede/línea?" (consecuencias: round_robin exige disciplina de disponibilidad) [en_sesion]
- `duracion_min`, `ventana_reserva`, `recordatorios[]` ← defaults de librería, solo se confirman. [en_sesion]
- Calendarios reales conectados (Google/Outlook de cada asesor) [checklist_habilitacion]

### `embudo_web`
- `paginas[].objetivo` ← se confirma contra la propuesta; contenido y piezas [asincrono_cliente]
- Dominio: ¿existe, apunta, quién lo controla? `evidencia_en_vivo` *(Kombat: combatmotos.com impreso en toda la pauta y sin destino)* [checklist_habilitacion]

### `segmento`
- `criterios[]` ← "¿A qué grupo de clientes le hablarían distinto si pudieran?" (default: segmentos del vertical) [en_sesion] — `hereda_entre_instancias: true` salvo criterio por línea.

### `tablero`
- `audiencia_funcion`, `frecuencia_revision` ← "¿Quién abre este tablero y en qué reunión se mira?" (default: dueño semanal, operación diaria). Un tablero sin reunión asociada es decoración. [en_sesion]
- `widgets[]` ← no se preguntan: se derivan de `metrica_que_habilita` de lo comprado (V3). Solo se confirma el orden de importancia. [en_sesion]

### `chatbot_ia` (por habilidad)
- Contexto del negocio (nombre comercial, actividad, líneas de producto, países/ciudades/sedes con su oferta, mercado objetivo, horarios del asesor humano, sitios web) ← lo responde el cliente solo, con los ejemplos del guion. *(Excel: toda la sección "Info general para el BOT".)* [brief_previo]
- `alcance[]` / `fuera_de_alcance[]` ← se **leen en voz alta** y el cliente los acepta; quedan en el acta. Es el ítem anti-disputa número uno. [en_sesion]
- Preguntas de captura ← hasta la cuota de la habilidad, y **cada una se marca `solo_captura` o `es_filtro`** (el filtro descarta por regla dura — cobertura, oferta — nunca por score; frontera del catálogo §3.1). Además: qué datos son mínimos para avanzar y cuáles se almacenan para seguimiento. *(Excel: variables de perfilación + datos mínimos + información a almacenar.)* [en_sesion]
- Metodología de entrega del lead al asesor ← "¿cómo quiere tu equipo recibir el lead transferido: asignación con tarea, alerta, llamada puente?" (default: asignación + alerta con resumen) [en_sesion]
- `base_conocimiento[]` ← por fuente: **quién la entrega, quién la actualiza, cada cuánto, y qué evento la rompe**. *(Kombat: la Z1100 y la Kal X 300 existían y el bot no las conocía; el cambio de Impulsa del lunes tumbó la sincronización del portafolio. Fuente sin dueño = bot desactualizado garantizado.)* [en_sesion + checklist_habilitacion]
- `criterio_escalamiento`, `handoff_a_funcion` ← "¿En qué momento exacto esto deja de ser del asistente y es de una persona? ¿Cómo se entera esa persona?" (default por habilidad; *Kombat: score alto → el asesor recibe alerta y llama él, el bot no estorba a un contado*) [en_sesion]
- `horario_activo` ← default 24/7 con manejo de fuera_de_horario de la guía de voz. [en_sesion]
- Personalidad, saludos, cierres y parámetros de conversación ← **no se especifican aquí**: heredan de `guia_de_voz`. Profundidades y fuentes por nivel: `catalogo-habilidades-ia.md` v1.1.

### `scoring`
- `variables[]` ← se presenta el modelo default (señal, puntos, fuente del dato) y se calibra con casos reales: "este cliente de la semana pasada, ¿cuántos puntos debía tener?" (*Kombat: moto 0–40, forma de pago 30 —contado directo, crédito 10 que sube a 30 con aprobación—, cuándo compra 20*) [en_sesion]
- `variables[].es_descalificadora` ← "¿Qué respuesta hace que NADIE deba invertir un minuto más?" (*Kombat: reportado + alta gama = ni Brilla lo salva*) [en_sesion]
- `umbrales[].accion` ← "Cuando alguien marca alto, ¿qué pasa en los primeros 5 minutos y quién?" (default: alerta + llamada inmediata, sin bot de por medio) [en_sesion]

### `migracion_datos`
- `fuentes[]` ← `inventario_verificado`: se abren los sistemas y se miran volúmenes reales. [en_sesion]
- `verificar_consentimiento` ← no negociable; el guion informa, no pregunta. Exportes y accesos [checklist_habilitacion]

### `propuesta_comercial` / `documento_firmable`
- `datos_requeridos[]` ← "¿Qué datos lleva hoy una cotización suya? Muéstrenme la última que enviaron." `evidencia_en_vivo` [en_sesion]
- `seguimiento` / `accion_post_firma` ← "Enviada la cotización, ¿qué pasa al día 2, al 5, al 10 si no responde?" (default: cadencia de librería) [en_sesion]
- Plantilla visual y textos [asincrono_cliente]

### `telefonia`
- ⚑ `numeros[]` + `enrutamiento` ← "¿Un número general, uno por asesor, o ambos?" (consecuencias: visibilidad vs. costo por línea; *Kombat: número general + número por asesor fue el cierre de la discusión*) [en_sesion]
- `grabacion.base_legal_declarada` ← el guion informa el requisito; sin base legal no se activa. [checklist_habilitacion]

### `integracion`
- `sistema`, `credenciales_requeridas[]` ← `inventario_verificado` + [checklist_habilitacion]
- `costo_externo` con `consumo_variable` ← corre `calculo_roi` en sesión con volúmenes del cliente. *(Kombat: TransUnion — la objeción "eso es un billete" murió con la cuenta hecha en vivo.)* [en_sesion]
- ⚑ Canal de mensajería (caso WhatsApp API vs. Business) ← consecuencias pre-redactadas: límites de conversaciones/día, plantillas tras 24 h, convivencia imposible API+Business en la misma línea, impacto en pauta a formulario. [en_sesion]

### `permisos_usuarios`
- `roles[]` ← se llena desde la ficha; en sesión solo: "¿quién puede ver TODO y quién solo lo suyo?" (*Kombat: la fuga de asesores sacando clientes a su WhatsApp personal es, en el fondo, un problema de visibilidad del dueño*) [en_sesion]

### `contenido` / `capacitacion`
- `piezas[].quien_produce` ← por pieza, con fecha. Lo que produce el cliente entra al checklist con dueño. [en_sesion → asincrono_cliente]
- `capacitacion.audiencia_funcion[]` ← se agenda en la misma sesión, no "después". [en_sesion]

---

## 5. Reglas de conducción del guion

**E1 — Proponer-primero.** Ningún ítem se pregunta en blanco si tiene
`default_metodologia`. El consultor presenta la recomendación y pide ajuste.

**E2 — Inventario solo verificado.** Cuentas, números, dominios, anuncios
corriendo y sistemas se registran viéndolos en pantalla, nunca de memoria, y
se registra también **lo excluido** con su razón *(Kombat: "usadas" conectada
pero fuera de alcance — sin registro, en 6 meses es una disputa)*.

**E3 — Problema en sesión, solución del sistema.** Cuando el cliente empieza a
diseñar la solución, el consultor lo regresa al problema y anota la idea como
insumo *(Kombat: "yo no quiero dar ninguna solución, sino que ustedes
entiendan el problema" — lo dijo el propio cliente)*.

**E4 — Ninguna decisión de arquitectura sin consecuencias leídas.** El
consultor lee `consecuencias` completas antes de aceptar la elección, y la
elección queda en el acta con las consecuencias que se leyeron.

**E5 — Lógica en vivo, copy en asíncrono.** La sesión nunca redacta mensajes.
Define qué dice cada mensaje (propósito y variables); el texto llega después,
redactado desde `guia_de_voz`, a aprobación con fecha límite.

**E6 — Todo aterriza en un campo o es change request.** Lo que surja en sesión
y no tenga `campo_destino` en el alcance comprado se anota en la sección de
change requests del acta, con la mejor voluntad y fuera del blueprint.

**E7 — Costo variable se decide con la cuenta hecha.** Ningún componente
`consumo_variable` se confirma sin correr su `calculo_roi` con los números
del cliente en pantalla.

---

## 6. Validaciones del blueprint

**S1 — Completitud.** Todo ítem `obligatorio` de todo componente del plan
tiene respuesta (propia o default aceptado) en cada instancia. Sin esto el
blueprint no pasa a construcción.

**S2 — Copy con dueño.** Todo `contenido_a_medida` termina en un ítem
`aprobacion_copy` con fecha y aprobador. Coherente con la regla global del
copy (schema v0.2 §1).

**S3 — Arquitectura con consecuencias.** Toda respuesta de tipo
`decision_arquitectura` guarda las `consecuencias` que se leyeron al decidir.

**S4 — Checklist con dueños.** El blueprint puede cerrarse con ítems de
habilitación pendientes, pero no con ítems de habilitación **sin dueño y sin
fecha**.

**S5 — Voz antes que copy.** `guia_de_voz.aprobada_por` no vacío antes de
activar cualquier `plantilla_mensaje` o `chatbot_ia`.

**S6 — Fuentes de conocimiento con dueño.** Toda entrada de
`base_conocimiento[]` tiene responsable de actualización y frecuencia. Un bot
con fuente huérfana es la reclamación de Kombat en cámara lenta.

---

## 7. Pendientes v0.2

- ~~`catalogo-habilidades-ia.md` no existe~~ **Resuelto 19-ago-2026**: existe
  como contrato v1.0 (doc. "Catálogo de habilidades IA (v1.0)" en el proyecto).
  El bloque de `chatbot_ia` de este schema toma alcance/fuera_de_alcance y
  niveles de allí.
- **Poblar los bloques sobre la librería compilada real** (este documento
  trabaja a nivel de tipo; los componentes concretos pueden necesitar
  `especificacion_extra`).
- **Calibrar contra otro vertical.** Toda la evidencia viene de concesionarios
  (Kombat). Una transcripción de un cliente de servicios o B2B diría si los
  defaults y las preguntas viajan.
- **Plantilla del acta de alcance** (vista firmable del blueprint: alcances,
  fuera-de-alcances leídos, decisiones con consecuencias, change requests).
- **Generador del guion**: el documento que el consultor lleva a la sesión,
  renderizado desde propuesta.json + estos bloques, ordenado por
  `posicion_journey` y agrupado por `quien_responde` — y su gemelo, el
  **brief renderizable** (formulario que el cliente llena solo, con los
  ejemplos por ítem que ya trae el Excel de levantamiento).
- **Migrar los ejemplos del Excel** "Promt BOT IA" (líneas de producto, sedes,
  mercado objetivo, estilos de saludo, cierres) como banco de ejemplos por
  ítem del brief — están escritos y probados; no reinventarlos.
