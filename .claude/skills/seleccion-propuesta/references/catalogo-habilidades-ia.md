# Catálogo canónico de habilidades del Asistente IA — contrato v1.1

Es el documento que `schema-componente.md v0.2` (`tipo: chatbot_ia`) referencia
y que el schema de especificación E4 necesita para especificar profundidades.
Toda venta, propuesta y spec de IA apunta aquí.

Decisiones de producto que este contrato fija (Jaime, 19-ago-2026):
N1 básico existe en Fundamental · el precalificador es exclusivo de
Inteligente · el negociador es habilidad propia · la preaprobación de crédito
entra como habilidad condicionada · **los bots standalone del brochure
(Informativo/Comercial) se repliegan a los planes** — el brochure ago-2026
queda como material de origen, no como taxonomía viva · **el Vendedor Virtual
es producto aparte, en piloto** (§3.12) · **filtrar por regla dura no es
precalificar** (§frontera en 3.1 y 3.5).

v1.1 incorpora tres fuentes de campo: el brochure AI Bots 8.2.1.1, las guías
de identidad del agente (Informativo/Comercial) y el Excel de levantamiento
"Promt BOT IA" — cuya estructura (ítem · momento en que se define ·
responsable · aplica-a-cuál-bot) validó en la práctica el diseño del guion E4.

Evidencia citada: *(Kombat)* = sesión 12-ago-2026 · *(AYC)* = piloto Activos
por Colombia · *(KYC #n)* = Voz del Cliente, 50 diagnósticos (doc.
Posicionamiento y Sistema de Mensaje).

---

## 0. Qué es una habilidad (y qué no)

- **Una habilidad = un componente `chatbot_ia`.** El asistente tiene amplitud
  (cuántas habilidades) y profundidad (qué tan lejos llega cada una); nunca se
  vende "el bot".
- **La profundidad no se declara: se deriva del plan.** Fundamental → N1,
  Avanzado → N2, Inteligente → N3, acotado por el `plan_entrada` de la
  habilidad: si el plan del cliente es menor que la entrada, la habilidad no
  existe para él. Una habilidad que entra en Inteligente solo existe en N3 —
  no hay versión rebajada.
- **Render:** todas las habilidades del plan se dibujan como **un solo nodo
  "Asistente IA"** en el lienzo (regla del schema v0.2 §1.2).
- **Voz:** ninguna habilidad define personalidad, saludo ni tono. Todo hereda
  de la `guia_de_voz` del cliente (E4 §2). Las habilidades definen *capacidad*,
  la guía define *carácter*.

### Regla de lenguaje (obligatoria en propuesta y lienzo)

El 56% del VoC rechaza "el bot que aleja" *(KYC #43 y 27 más)*. Por eso:

- La palabra **"bot" no se usa nunca** de cara al cliente.
- **N1 no se presenta como asistente**: se vende como *"respuesta inmediata"*
  (nadie objeta que le contesten rápido). La palabra **"asistente" se reserva
  para N2 en adelante**, cuando la IA ya ejecuta.
- Toda pieza de venta de IA lleva la regla transversal del posicionamiento:
  **la IA no reemplaza al humano con el cliente listo** — atiende al que solo
  está mirando y entrega al equipo el que sí va a comprar (bisagra de
  enrutamiento por temperatura, Pilar 2 ↔ Pilar 3).

### Reglas universales del asistente (defaults duros — no se preguntan al cliente)

Vienen del Excel de levantamiento (secciones "Restricciones finales" y "Reglas
de comunicación") y aplican a **toda habilidad, todo nivel, todo cliente**. El
guion E4 las informa; no las negocia:

- **No inventa información** — si la base de conocimiento no lo cubre, lo dice
  y escala.
- **No promete precios finales ni afirma disponibilidad sin validar** contra la
  fuente.
- **No menciona sistemas internos** (CRM, IA, modelos, automatizaciones) — se
  declara asistente si la guía de voz lo indica, pero jamás explica su
  plomería.
- **Pregunta una cosa a la vez.**
- **No sale de su rol** ni opina fuera del negocio del cliente.
- **Respeta el máximo de líneas por respuesta** definido en la guía de voz.
- **Todo descarte lleva salida digna** (mensaje de cierre, nunca silencio).

### Costo variable de IA (transversal a todas las habilidades)

El consumo de IA es `costo_externo: consumo_variable` de todo componente
`chatbot_ia`: cada plan incluye un monto mensual de créditos y el exceso se
cobra por consumo (tokens de entrada/salida según modelo). La voz suma costo
por minuto/país y los mensajes outbound fuera de ventana de 24 h suman costo
de plantilla por país. Los valores viven en el **registro de costos
variables** (por crear — hoy la referencia es el brochure ago-2026, pp. 8–9);
la propuesta los declara con la etiqueta del carril de integraciones, y la
spec E4 corre `calculo_roi` cuando el volumen del cliente lo amerita.
**Pendiente de producto:** fijar los créditos incluidos por plan
(el brochure traía $15/$30/$50 USD/mes por bot; al replegarse a planes, la
cifra debe redefinirse por plan).

---

## 1. Gramática de los niveles

La misma prueba de pertenencia de la matriz de fronteras, aplicada a la IA:

| Nivel | Verbo | Qué puede hacer | Qué NO puede hacer |
|---|---|---|---|
| **N1** | **Responde** | Contesta al instante con contenido aprobado y estático. | No escribe en el CRM, no agenda, no clasifica, no conoce al contacto. |
| **N2** | **Ejecuta** | Actúa cuando el cliente final actúa: escribe en el CRM, enruta, agenda, clasifica respuestas, usa el contexto del contacto. | No decide prioridades, no actúa por silencio, no consulta datos vivos. |
| **N3** | **Decide** | Actúa cuando nadie actúa o con criterio propio: prioriza la fila, usa datos vivos del catálogo, retoma frío, recomienda, preaprueba. | Lo que su `fuera_de_alcance` diga — y ese texto se imprime en la propuesta. |

La escalera es la de los planes: *responde → ejecuta → decide* es la versión IA
de *registra → automatiza el presente → persigue el futuro*.

---

## 2. Schema de la entrada de catálogo

| Campo | Notas |
|---|---|
| `id` | slug estable; es lo que `chatbot_ia.habilidad` referencia. |
| `nombre_cliente` | Cómo se llama en el lienzo y la propuesta. |
| `que_hace` | Una frase. |
| `plan_entrada` | fundamental · avanzado · inteligente. |
| `niveles.N*` | Solo los niveles ≥ `plan_entrada`. Cada uno: `alcance[]`, `fuera_de_alcance[]` (**obligatorio, se imprime**), `que_desbloquea` (frase de venta del salto). |
| `base_conocimiento_requerida[]` | Por fuente: quién la entrega, quién la actualiza, vigencia. Hereda la regla S6 de E4: fuente sin dueño = habilidad que no se activa. |
| `escalamiento_default` | Criterio + `handoff_a_funcion` recomendados; la sesión E4 los calibra. |
| `metricas[]` | Lo que la habilidad vuelve medible (alimenta `metrica_que_habilita`). |
| `prerequisitos[]` | Reglas o aprobaciones sin las cuales no se activa (O-01, habeas data…). |
| `aplica_si` | Condición de perfil; vacío = universal. |
| `costo_externo` | Solo si la habilidad consume servicios pagados por uso. |
| `componentes[]` | Ids de librería que hoy implementan la habilidad ("—" = por crear). |

---

## 3. Las once habilidades

### 3.1 `recepcionista`
- **nombre_cliente:** "Recepción inmediata" (N1) / "Recepcionista digital" (N2+)
- **que_hace:** Recibe toda conversación entrante, la clasifica y la pone en manos correctas.
- **plan_entrada:** fundamental
- **N1 — responde:** bienvenida inmediata con horario y qué esperar. *Fuera de alcance:* no escribe en CRM, no distingue intenciones, no agenda.
- **N2 — ejecuta:** detecta intención, crea/actualiza el contacto con origen, enruta al pipeline y función correctos. Hace las **preguntas de captura** definidas por el cliente (hasta la cuota), y cada pregunta se configura como `solo_captura` o `es_filtro` — el filtro descarta por **regla dura** (cobertura de ciudad, producto fuera de oferta, dato mínimo ausente), con salida digna. En la práctica, de 4 preguntas de captura suelen filtrar 1–2; el cliente elige cuáles. *Fuera de alcance:* no infiere ni puntúa interés, no etiqueta temperatura, no prioriza la fila, no negocia. **Frontera con el precalificador (decisión 19-ago):** filtrar por regla no es precalificar — descartar al que no tiene cobertura es ejecutar una regla (N2); conversar para inferir cuánto vale el lead es decidir (N3). *Desbloquea:* "deje de contestar usted".
- **N3 — decide:** prioriza por score y contexto; el lead caliente salta la fila y dispara alerta al asesor. *(Kombat: score verde → el asesor recibe alerta y llama él; la IA no estorba a un contado.)* *Fuera de alcance:* no vende ni cotiza.
- **base_conocimiento:** mapa de intenciones y funciones (lo produce E4, dueño: Ropofy).
- **escalamiento_default:** intención no reconocida 2 veces → humano de guardia.
- **metricas:** tiempo_primera_respuesta, conversaciones_recibidas_ia, distribucion_por_intencion.
- **componentes:** gestion-ruteo-intencion (parcial) · componente chatbot dedicado **por crear**.

### 3.2 `informativo`
- **nombre_cliente:** "Respuestas al instante" (N1) / "Asistente que sabe del negocio" (N2+)
- **que_hace:** Responde preguntas frecuentes y de proceso desde la base de conocimiento aprobada.
- **plan_entrada:** fundamental
- **N1 — responde:** FAQs desde base estática aprobada. *Fuera de alcance:* solo responde lo que está en la base; no sabe quién pregunta.
- **N2 — ejecuta:** responde con contexto del contacto (qué preguntó antes, en qué etapa va) y registra la duda en el CRM. *Fuera de alcance:* no consulta inventario ni precios vivos.
- **N3 — decide:** responde con **datos vivos del catálogo** — existencia, disponibilidad, atributos. *(Kombat: la Z1100 y la Kal X 300 existían y la IA no las conocía; el cambio de Impulsa del lunes tumbó la sincronización. N3 sin fuente viva con dueño es la reclamación garantizada — de ahí la validación H5.)* *Fuera de alcance:* no promete disponibilidad que la fuente no confirme; no cotiza condiciones comerciales.
- **base_conocimiento — taxonomía de fuentes por nivel** (del Excel de levantamiento): **N1** = FAQs aprobadas (cuota por plan: 10/25/50 redactadas por Ropofy, matriz §4) + texto enriquecido de productos/servicios; **N2** = lo anterior + sitios web oficiales declarados (el asistente consulta las URLs aprobadas); **N3** = lo anterior + catálogo vivo sincronizado (online o JSON/tabla) con dueño y frecuencia declarados.
- **escalamiento_default:** dos "no sé" seguidos o solicitud explícita → humano.
- **metricas:** preguntas_resueltas_ia, tasa_no_se, tasa_escalamiento.
- **componentes:** gestion-chatbot-precalificacion (parte informativa — ver corrección C2).

### 3.3 `agendador`
- **nombre_cliente:** "Citas que se agendan solas"
- **que_hace:** Convierte la conversación en cita sobre los calendarios reales del equipo.
- **plan_entrada:** avanzado
- **N2 — ejecuta:** ofrece horarios del calendario correcto (por función/sede/línea), agenda y confirma en la conversación. *Fuera de alcance:* no decide el tipo de cita por el cliente; no mueve citas existentes.
- **N3 — decide:** reagenda ante no-show o cancelación, optimiza huecos, reordena por prioridad de score. *Fuera de alcance:* nunca agenda fuera de las reglas de disponibilidad; no cancela unilateralmente.
- **base_conocimiento:** calendarios conectados (checklist de habilitación E4), reglas de asignación.
- **escalamiento_default:** conflicto de agenda o cliente VIP → coordinador.
- **metricas:** citas_agendadas_ia, tasa_no_show, reagendadas_ia.
- **componentes:** **por crear** (hoy `calendario` existe como tipo, la habilidad conversacional no).

### 3.4 `reactivador`
- **nombre_cliente:** "El que atiende cuando 400 dormidos contestan el mismo día"
- **que_hace:** Absorbe el pico de respuestas de las campañas de reactivación sin ahogar al equipo.
- **plan_entrada:** avanzado
- **N2 — ejecuta:** clasifica cada respuesta de la oleada (interesado / no / más tarde / cambió de interés), actualiza la línea de interés y rutea. *Fuera de alcance:* no recalifica temperatura completa, no renegocia, no insiste por su cuenta.
- **N3 — decide:** decide a quién reintentar, cuándo y con qué mensaje; descarta con motivo registrado. *Fuera de alcance:* jamás toca contactos sin consentimiento verificado (regla de `migracion_datos`).
- **base_conocimiento:** motivos de descarte del vertical, campaña activa.
- **escalamiento_default:** interés transaccional confirmado → pipeline + asesor (así está en la librería).
- **metricas:** respuestas_atendidas_ia, reactivados_a_pipeline, descartados_con_motivo.
- **componentes:** reactivacion-precalificacion-ia (**renombrar** — ver corrección C4).

### 3.5 `precalificador` — exclusiva de Inteligente
- **nombre_cliente:** "Tu equipo solo habla con quien sí va a comprar"
- **que_hace:** Conversa con todo lead entrante, hace las preguntas de triage, etiqueta interés y temperatura, y alimenta el scoring.
- **plan_entrada:** inteligente
- **N3 — decide:** ejecuta el triage del vertical *(Kombat: forma de pago, cuándo compra, modelo de interés)*, aplica descalificadoras con **salida digna** (el descartado recibe cierre respetuoso y el asesor nunca lo ve), verifica leads de terceros al ingreso *("Nos llegó tu información de Auteco, ¿me confirmas que este es el vehículo que buscas?" — Kombat: el 90% de los leads "alta gama" de Impulsa no querían alta gama)*, y entrega al humano el lead desmenuzado *("no quiero que el asesor pregunte lo que la IA debió preguntar" — Cristian, Kombat)*.
- **Fuera de alcance (se imprime):** no aprueba créditos, no promete precio ni disponibilidad, no descarta sin mensaje de salida, no reemplaza al asesor con el lead caliente.
- **Qué NO exige esta habilidad:** el filtrado por regla dura (ciudad, oferta, dato mínimo) — eso lo hace el `recepcionista` N2 desde Avanzado. El precalificador empieza donde la regla termina: donde hay que **inferir** — presupuesto real, urgencia, temperatura, score.
- **base_conocimiento:** preguntas de triage por línea (E4 · scoring), catálogo de descalificadoras, variantes de saludo por punto de ingreso (guia_de_voz).
- **escalamiento_default:** umbral alto de score → alerta + llamada del asesor en ≤5 min.
- **metricas:** leads_precalificados_ia, tasa_descalificacion, tasa_escalamiento, temperatura_distribucion.
- **prerequisitos:** scoring configurado; O-01 (tono y límites aprobados).
- **demanda VoC:** 14/50 diagnósticos la piden con esas palabras *(KYC #37, #26, #45…)*. Es la habilidad que vende el plan.
- **componentes:** parte precalificadora de gestion-chatbot-precalificacion → **se separa** (corrección C2).

### 3.6 `asesor_recomendador` — exclusiva de Inteligente
- **nombre_cliente:** "Te ayuda a escoger, no solo a preguntar"
- **que_hace:** Recomienda ítems del catálogo vivo según la necesidad declarada.
- **plan_entrada:** inteligente
- **N3 — decide:** pregunta la necesidad antes que el producto *(Kombat: "¿ya sabes qué moto quieres o quieres que te ayudemos a escoger?" — el ~30% no sabe; y la pregunta del buen vendedor: "¿qué otras has visto y qué no te gustó?")*, propone 2–3 opciones del catálogo con su porqué, registra la preferencia.
- **Fuera de alcance:** solo recomienda del catálogo vivo — nunca inventa disponibilidad; no compara con la competencia; no da asesoría financiera.
- **base_conocimiento:** catálogo sincronizado con atributos de recomendación (dueño y vigencia obligatorios, H5), criterios de necesidad del vertical.
- **escalamiento_default:** cliente indeciso tras 2 rondas o ticket alto → asesor humano.
- **metricas:** recomendaciones_entregadas, interes_por_item, conversion_recomendacion_a_cita.
- **componentes:** **por crear** (la matriz la lista; la librería aún no la tiene).

### 3.7 `retomador` — exclusiva de Inteligente
- **nombre_cliente:** "La conversación que se enfrió la retoma alguien que recuerda todo"
- **que_hace:** Revive conversaciones frías con memoria del hilo, actualiza la calificación y reagenda.
- **plan_entrada:** inteligente
- **N3 — decide:** se dispara por silencio/enfriamiento (nunca por acción — esa es la línea de Inteligente), retoma citando el contexto real del hilo, actualiza temperatura, reagenda o rutea.
- **Fuera de alcance:** no cambia condiciones de lo conversado (eso es del `negociador`); no insiste más allá de la cadencia aprobada; no retoma a quien pidió no ser contactado.
- **base_conocimiento:** cadencia de retoma aprobada (O-01), historial del contacto.
- **escalamiento_default:** respuesta con intención de compra → asesor con alerta.
- **metricas:** conversaciones_reinyectadas, recuperados_por_ia.
- **componentes:** nutricion-reinyeccion-ia (asignarle `habilidad: retomador`).

### 3.8 `negociador` — exclusiva de Inteligente *(nueva en v1.0)*
- **nombre_cliente:** "Las propuestas que nadie retomaría las retoma alguien que sí sabe qué ofrecer"
- **que_hace:** Retoma propuestas frías o en visto: resuelve dudas de la propuesta, recuerda vigencia y ajusta **condiciones estándar pre-aprobadas**.
- **plan_entrada:** inteligente
- **N3 — decide:** responde dudas de la propuesta enviada, gestiona vigencia y renegocia solo dentro del tarifario de concesiones aprobado (O-01): qué puede ofrecer, en qué orden, y qué jamás.
- **Fuera de alcance (se imprime, es el ítem más sensible del catálogo):** nunca inventa descuentos ni condiciones fuera de la lista aprobada; no modifica la propuesta formal — propone y el sistema regenera; escala toda contra-oferta no contemplada.
- **base_conocimiento:** la propuesta viva del contacto + reglas de negociación firmadas por el cliente (prerequisito duro).
- **escalamiento_default:** contra-oferta fuera de reglas o señal de cierre → closer con alerta.
- **metricas:** propuestas_retomadas_ia, cierres_asistidos_ia, concesiones_usadas.
- **prerequisitos:** O-01 reglas de negociación aprobadas y versionadas.
- **componentes:** cierre-recuperacion-ia (asignarle `habilidad: negociador`).
- **Por qué es habilidad propia y no un modo del retomador:** su riesgo (dar plata) y su fuera_de_alcance son de otra especie; mezclarla sería la confusión amplitud/profundidad que el schema prohíbe.

### 3.9 `recepcionista_voz` — exclusiva de Inteligente
- **nombre_cliente:** "La llamada de las 9 pm la contesta alguien que toma el caso completo"
- **que_hace:** Contesta llamadas fuera de horario o en desborde, radica el caso completo en el CRM y agenda el retorno.
- **plan_entrada:** inteligente
- **N3 — decide:** atiende, identifica intención, captura datos del caso, radica y agenda; el equipo llega y ya está registrado.
- **Fuera de alcance:** no cierra ventas por teléfono; no da información de datos personales de terceros; no promete tiempos que el calendario no confirme.
- **base_conocimiento:** guion de radicación por tipo de caso; hereda voz (incluye manejo de insulto/silencio de la guía).
- **escalamiento_default:** urgencia declarada → llamada al humano de guardia.
- **metricas:** llamadas_fuera_horario_atendidas, casos_radicados_por_ia.
- **prerequisitos:** gestion-telefonia-llamadas en el plan; grabación con base legal declarada.
- **componentes:** gestion-llamada-ia-fuera-horario (corrección C5: quitar `profundidad: 2`).

### 3.10 `redactor_resenas` — exclusiva de Inteligente
- **nombre_cliente:** "Responder cien reseñas cuesta lo mismo que responder una"
- **que_hace:** Responde reseñas públicas con tono de marca; las negativas siempre pasan por humano.
- **plan_entrada:** inteligente
- **N3 — decide:** responde positivas automáticamente; redacta borrador de las ≤3★ y lo entrega al coordinador.
- **Fuera de alcance:** jamás publica respuesta a una negativa sin aprobación; nunca discute con el cliente en público; no ofrece compensaciones.
- **base_conocimiento:** guia_de_voz + política de respuesta por tipo de queja.
- **escalamiento_default:** ≤3★ → borrador a coordinador (así está en la librería).
- **metricas:** respuestas_generadas_ia, tiempo_respuesta_resena_ia.
- **componentes:** reputacion-respuestas-ia (asignarle `habilidad: redactor_resenas`).

### 3.11 `preaprobador_credito` — exclusiva de Inteligente, condicionada *(nueva en v1.0)*
- **nombre_cliente:** "El estudio de crédito empieza en el chat, no en la visita"
- **que_hace:** Con autorización del titular, consulta el buró y devuelve un semáforo de viabilidad antes de que el asesor invierta un minuto.
- **plan_entrada:** inteligente
- **aplica_si:** vertical con venta financiada (vehículos, inmobiliario con crédito, retail de ticket alto).
- **N3 — decide:** pide autorización de tratamiento de datos en el chat *(habeas data explícito y registrado — no negociable)*, solicita cédula, consulta el buró, aplica el semáforo con las variables preconfiguradas por el cliente y actúa: verde → agenda estudio con alerta al asesor; amarillo → ruta de documentación; rojo → salida digna y descarte con motivo. *(Kombat: cierra la trampa del autorreporte — "¿estás reportado?" "no" … y sí lo estaba, "uf, bastante".)*
- **Fuera de alcance (se imprime):** es un **pre-filtro, no una aprobación de crédito** — el semáforo nunca se comunica como decisión de una entidad; jamás consulta sin autorización registrada; no guarda el documento más allá de la política declarada.
- **base_conocimiento:** variables del semáforo por entidad (las preconfigura el cliente en E4), textos legales aprobados.
- **escalamiento_default:** verde → asesor en ≤5 min; disputa del resultado → humano siempre.
- **metricas:** consultas_buro, tasa_preaprobados, costo_consulta_acumulado, ahorro_gestion_estimado.
- **costo_externo:** `consumo_variable` — consulta de buró (~$400–500 tercero + ~$200–400 Ropofy por consulta, valores ago-2026 a confirmar por contrato). **Su spec E4 corre `calculo_roi` obligatorio** *(Kombat: ~800 consultas × $700 ≈ $560k/mes contra las horas de asesor gestionando reportados — la objeción murió con la cuenta en pantalla)*.
- **prerequisitos:** contrato del cliente con el buró o intermediación Ropofy; integración de consulta; política de datos publicada.
- **componentes:** **por crear** (gestion-preaprobacion-credito, integración de buró como componente `integracion` aparte).

### 3.12 Familia transaccional — `estado: piloto`, producto aparte

El **Vendedor Virtual** no se repliega a los planes: es un producto propio, hoy
en piloto con un solo cliente (+3 semanas de pruebas a ago-2026). Su
complejidad es de otra clase — vectorización de inventarios, orquestación con
n8n, conexiones a medida — y por eso aplica la misma lógica de la regla V11
del schema de componentes: **lo no nativo no viaja dentro del plan.** Sus
habilidades se catalogan desde ya para que alcance y fuera-de-alcance no se
improvisen cuando salga del piloto, pero ninguna tiene `plan_entrada`: su
plan es "ninguno", se cotiza como producto.

| Habilidad (piloto) | Qué hará | Fuera de alcance ya declarado |
|---|---|---|
| `tomador_pedidos` | Toma el pedido completo en la conversación contra el inventario vectorizado. | No modifica precios; no confirma sin validar existencia. |
| `confirmador_pagos` | Verifica y confirma pagos recibidos, actualiza el estado del pedido. | No procesa el cobro (eso es de la pasarela); no reembolsa. |
| `gestor_inventario` | Consulta y reserva sobre inventario vivo durante la conversación. | No ajusta stock maestro; no promete lo que la fuente no confirme. |
| Manejo de devoluciones | **Fuera de alcance incluso del Vendedor Virtual** (así lo declara el propio brochure) — se radica y escala a humano. | — |

Prerrequisitos ya conocidos del piloto: inventario en formato estructurado
(JSON/tabla), pipeline de vectorización, flujo n8n, y reglas de negocio de
pedido/pago firmadas por el cliente (misma clase de riesgo que H6).

---

## 4. Matriz consolidada por plan

Sustituye a la tabla §3 de matriz-fronteras v1.0 (ver corrección C1).

| Habilidad | Fundamental | Avanzado | Inteligente |
|---|---|---|---|
| recepcionista | N1 responde | N2 enruta y escribe en CRM | N3 prioriza la fila |
| informativo | N1 FAQs estáticas | N2 con contexto del contacto | N3 con catálogo vivo |
| agendador | — | N2 agenda en la conversación | N3 reagenda y optimiza |
| reactivador | — | N2 clasifica la oleada | N3 decide a quién reintentar |
| **precalificador** | — | — | N3 triage, salida digna, verificación de terceros |
| **asesor_recomendador** | — | — | N3 recomienda del catálogo vivo |
| **retomador** | — | — | N3 revive la conversación fría |
| **negociador** | — | — | N3 condiciones estándar pre-aprobadas |
| **recepcionista_voz** | — | — | N3 contesta y radica llamadas |
| **redactor_resenas** | — | — | N3 responde reseñas con criterio |
| **preaprobador_credito** ⚑ | — | — | N3 semáforo de buró *(condicionada + consumo variable)* |

**Siete habilidades son exclusivas de Inteligente** (antes cinco). Fundamental
incluye respuesta inmediata N1 en dos habilidades — y **no se comercializa como
asistente** (regla de lenguaje §0): el argumento del salto a Avanzado ("deje de
contestar usted") queda intacto porque N1 responde pero no ejecuta. La familia
transaccional (§3.12) no aparece en esta matriz a propósito: es producto
aparte, no plan.

**Cuotas nuevas para la matriz de fronteras** (heredadas del brochure, valores
por confirmar al fijarlas por plan): **rondas de entrenamiento inicial** del
asistente (brochure: 4/6) y **ajustes post-activación por mes** (brochure:
4/6/8). Ambas cuentan entregables, no horas — consistentes con la decisión
"sin boosters ni bolsas de horas".

---

## 5. Correcciones que este catálogo obliga (librería y matriz)

- **C1 — matriz-fronteras.md:** §3 se reemplaza por la matriz §4 de aquí. La
  viñeta 1 de §5 ("Fundamental no tiene IA") se reescribe: *"Fundamental
  incluye respuesta inmediata (N1): responde, no ejecuta. No se comercializa
  como asistente — esa palabra y ese argumento pertenecen a Avanzado."*
- **C2 — gestion-chatbot-precalificacion se divide en dos componentes.** Su
  alcance actual `[faq_proceso, requisitos, precalificacion, estado_catalogo]`
  mezcla dos habilidades, contra la regla "un componente = una habilidad":
  (a) `gestion-asistente-informativo` — habilidad `informativo`, plan
  **avanzado**, alcance faq_proceso + requisitos + estado_catalogo (N2);
  (b) `gestion-precalificador` — habilidad `precalificador`, plan
  **inteligente**. Revisar el mapeo de fugas: el cierre que dependa de
  *precalificar* (parte de F-08/F-14) viaja con (b) a Inteligente; lo que
  cierre *atención de volumen* se queda en (a). Actualizar `depende_de` de
  cierre-recuperacion-ia y nutricion-reinyeccion-ia al id nuevo que corresponda.
- **C3 — Campo `habilidad` faltante** en 4 componentes existentes:
  reputacion-respuestas-ia → `redactor_resenas` · cierre-recuperacion-ia →
  `negociador` · nutricion-reinyeccion-ia → `retomador` ·
  reactivacion-precalificacion-ia → `reactivador`.
- **C4 — reactivacion-precalificacion-ia se renombra** (sugerido:
  `reactivacion-absorcion-oleadas`): en Avanzado su alcance es reactivador N2
  (clasificar, actualizar línea, rutear); "recalificar" completo es N3. El
  nombre actual promete precalificación en un plan donde esa habilidad ya no
  existe.
- **C5 — gestion-llamada-ia-fuera-horario:** eliminar `profundidad: 2` (la
  profundidad se deriva del plan; el componente es Inteligente → N3, como ya
  dice la propia tabla del módulo en su línea 755).
- **C6 — Componentes por crear:** recepcionista de chat como `chatbot_ia`
  propio, `agendador` conversacional, `asesor_recomendador`,
  `gestion-preaprobacion-credito` + su `integracion` de buró.

---

## 6. Validaciones

**H1 — Habilidad canónica.** Todo componente `chatbot_ia` declara `habilidad`
con un id de este catálogo. Sin excepciones ni texto libre.

**H2 — Profundidad derivada.** Ningún componente declara `profundidad`; se
calcula del plan y del `plan_entrada`. (Hoy la viola C5.)

**H3 — Plan coherente.** `plan_minimo` del componente ≥ `plan_entrada` de su
habilidad. (Hoy la viola la mitad precalificadora de C2.)

**H4 — Fuera de alcance impreso.** El `fuera_de_alcance` del nivel vendido
acompaña a la habilidad en propuesta y acta, siempre.

**H5 — Datos vivos con dueño.** Toda habilidad que consulte datos vivos
(informativo N3, asesor_recomendador, negociador, preaprobador) exige fuente
con responsable, frecuencia y evento-que-la-rompe declarados (E4 · S6). Sin
dueño de fuente, la habilidad se vende en su nivel inferior o no se vende.

**H6 — Reglas antes que autonomía.** `negociador` y `preaprobador_credito` no
se activan sin sus reglas aprobadas y versionadas (tarifario de concesiones;
variables de semáforo + habeas data). La firma de esas reglas es un ítem del
acta E4, no un correo suelto.

**H7 — Una habilidad, un componente.** Ningún componente lista alcances de dos
habilidades distintas. (Hoy la viola C2.)

---

## 7. Pendientes v1.2

- Confirmar con producto el **alcance real de la IA de calificación** — el
  propio doc de posicionamiento lo marca como no auditado (⚠️ Pilar 3, §8).
- Verificar los **ids de fugas** citados en C2 contra el catálogo de fugas al
  ejecutar la corrección.
- Precios del preaprobador por contrato con el buró (los valores citados son
  de la conversación Kombat, no de tarifario).
- Cuota de **idiomas** por plan (el schema la contempla; ningún documento la
  fija).
- Calibrar `asesor_recomendador` y `preaprobador_credito` contra un vertical
  no automotor antes de generalizarlos.
- **Registro de costos variables** como archivo propio (créditos de IA por
  plan, tarifas de voz por país, plantillas outbound por país) — hoy la fuente
  es el brochure ago-2026 y quedará desactualizada.
- **Créditos de IA incluidos por plan** — decisión de producto pendiente tras
  el repliegue de los bots standalone.
- Graduación del **Vendedor Virtual**: cuando el piloto cierre, definir sus
  componentes de librería, precio y si alguna habilidad transaccional simple
  (p. ej. `gestor_inventario` de solo consulta) puede bajar a los planes.
- Comunicar la **descontinuación del brochure** como línea de venta: sus
  números de precio/setup no deben volver a circular; el material visual puede
  reutilizarse para el asistente de los planes.
