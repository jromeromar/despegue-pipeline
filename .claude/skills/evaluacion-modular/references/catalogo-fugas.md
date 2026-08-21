# Catálogo de fugas — v0.2

Derivado de 264 dolores en 53 diagnósticos (mayo–agosto 2026), actualizado con
el piloto Activos por Colombia. Contraparte de `cierra_fugas` / `mitiga_fugas`
del schema de componente.

---

## 1. Seis categorías, no una

| Categoría | Qué es | Cómo entra a la propuesta |
|---|---|---|
| `fuga` | Dinero que se escapa hoy, medible | Se cuantifica; se cierra o se mitiga con componentes |
| `ceguera` | Imposibilidad de medir | No se cuantifica la pérdida sino el gasto sin evaluar |
| `restriccion` | Límite técnico o de plataforma | Prerrequisito del plan, no fuga |
| `objecion` | Miedo o mala experiencia previa | Narrativa y garantías, nunca un componente |
| `carencia_demanda` | No hay flujo que perder | Se atiende antes que cualquier fuga de conversión |
| `friccion_propia` | Un activo del cliente destruye conversión por diseño (ej: registro de 14 pasos en su web) | Se nombra con evidencia; lo corrige el cliente, no Ropofy. Contamina toda tasa de conversión que se mida después, y eso se declara. |

Mezclarlas produce dos errores: monetizar lo no monetizable y vender
componentes contra miedos.

---

## 2. Schema de la fuga

| Campo | Notas |
|---|---|
| `id` | Estable. Los componentes apuntan aquí. |
| `nombre_cliente` | Lenguaje de negocio. Va en la sección "Fugas" de la propuesta. |
| `categoria` | fuga · ceguera · restriccion · objecion · carencia_demanda |
| `modulo` | Módulo interno responsable de cerrarla. |
| `etapa_embudo` | Dónde ocurre. Clave para el antidoble-conteo (§4). |
| `sintoma` | Lo que el consultor escucha literalmente. |
| `causa_raiz` | Mecanismo, no síntoma. |
| `formula` | Cuantificación con datos del guión. Vacío si no aplica. |
| `datos_requeridos` | Campos que la fórmula necesita. |
| `frecuencia_observada` | Casos sobre 53. Calibra severidad por defecto. |
| `sujeto_embudo` | demandante · oferente. Por defecto demandante. |
| `cerrada_por` | [id_componente] que eliminan la causa. Se llena al poblar la librería. |
| `mitigada_por` | [id_componente] que la reducen o la hacen medible sin eliminar la causa. |
| `cerrable_por_ropofy` | bool. Falso cuando la causa la controla un tercero o una decisión de negocio del cliente. Una fuga con falso y sin `mitigada_por` solo se declara. |
| `aplica_si` | Condición sobre la ficha de perfil, si es condicional. |

---

## 3. Catálogo

### Categoría: fuga

**F-01 · El lead que no responde se pierde para siempre**
`modulo: nutricion` · `etapa: post_primer_contacto` · **~25/53**
- Síntoma: "se hace muy poco seguimiento", "si no contestan, hasta ahí",
  "depende de la memoria del asesor", "es un poco desgastante".
- Causa: no existe secuencia; el seguimiento compite con la atención del día.
- Fórmula: `(leads_mes − clientes_nuevos_mes) × tasa_recuperacion × margen_por_cliente`
- Datos: leads mensuales, clientes nuevos, ticket, margen bruto.
- Nota: usar rango conservador de recuperación, nunca un punto único.

**F-02 · Los mensajes fuera de horario no se atienden**
`modulo: gestion` · `etapa: primer_contacto` · **~14/53**
- Síntoma: "después de las 5 se pierden", "llegan de noche y nadie responde",
  demoras de 10 a 15 horas, respuestas "a veces días".
- Causa: atención humana con horario contra demanda 24/7.
- Fórmula: `leads_fuera_horario × (conversion_atendido − conversion_desatendido) × margen_por_cliente`
- Datos: % de leads fuera de horario, horario real, conversión base.

**F-03 · La respuesta llega tarde y el lead ya se enfrió**
`modulo: gestion` · `etapa: primer_contacto` · **~12/53**
- Síntoma: demora promedio de 30 minutos a horas; "pérdida de impulso de decisión".
- Causa: sin asignación automática ni SLA; el primero que ve el mensaje responde.
- Fórmula: `leads_mes × %_respondidos_despues_de_5min × delta_conversion × margen_por_cliente`
- Datos: tiempo de primera respuesta, % bajo 5 minutos.

**F-04 · La cotización enviada nunca se retoma**
`modulo: cierre` · `etapa: propuesta` · **~6/53**
- Síntoma: "muchas cotizaciones quedan sin respuesta y no se reactivan".
- Causa: no hay tarea ni secuencia atada al envío de propuesta.
- Fórmula: `(propuestas_mes − cierres_mes) × tasa_recuperacion_propuesta × margen_por_cliente`
- Datos: propuestas generadas, clientes nuevos, margen.
- Nota: la fuga más rentable de cerrar — intención de compra ya demostrada.

**F-05 · La cita agendada no se presenta**
`modulo: gestion` · `etapa: agendamiento` · **~5/53**
- Síntoma: "se les caen muchas citas", "no confirman y pierden el cupo",
  visitas innecesarias por falta de filtro previo.
- Causa: sin recordatorios ni confirmación; sin precalificación antes de agendar.
- Fórmula: `no_shows_mes × conversion_demo_a_cierre × margen_por_cliente`
- Datos: demos agendadas, demos realizadas, conversión demo→cierre.
- `aplica_si`: el proceso incluye cita, visita o demo.

**F-06 · La asignación azarosa deja leads sin dueño**
`modulo: gestion` · `etapa: primer_contacto` · **~10/53**
- Síntoma: "responde el primero que lo ve", una asesora recibe la mayoría,
  el cliente elige a qué vendedor escribir, línea compartida entre asesores.
- Causa: canal único sin ruteo; nadie es responsable de un lead específico.
- Fórmula: `leads_mes × %_sin_dueño_identificable × conversion_base × margen_por_cliente`
- Datos: número de líneas, mecanismo de asignación, leads mensuales.

**F-07 · El lead nuevo pierde contra el cliente recurrente**
`modulo: gestion` · `etapa: primer_contacto` · **~4/53**
- Síntoma: "un mismo vendedor atiende leads nuevos y clientes fijos, prioriza
  los recurrentes y deja fríos los potenciales".
- Causa: una sola cola para dos procesos con urgencias distintas.
- Fórmula: `leads_nuevos_mes × %_desatendido_por_prioridad × conversion_base × margen`
- `aplica_si`: la misma función atiende adquisición y cuentas activas.

**F-08 · El volumen desborda la capacidad y se responde a medias**
`modulo: gestion` · `etapa: primer_contacto` · **~15/53**
- Síntoma: 50–70 mensajes diarios sin alcanzar a responder; 400–700 leads
  diarios "todo manual"; campañas detenidas por no dar abasto.
- Causa: capacidad humana fija contra demanda variable.
- Fórmula: `(leads_mes − capacidad_mensual_equipo) × conversion_base × margen_por_cliente`
- Datos: leads mensuales, capacidad por asesor, número de asesores.
- Nota: cuando esta fuga es dominante, el cliente **ya frenó la pauta**. El
  argumento no es solo recuperar, es desbloquear inversión.

**F-09 · Cada asesor vende a su manera**
`modulo: gestion` · `etapa: transversal` · **~7/53**
- Síntoma: "no tienen embudo explícito, el proceso está tácito y variable".
- Causa: sin etapas definidas no hay estándar ni auditoría posible.
- Fórmula: `dispersion_conversion_entre_asesores × leads_mes × margen`
- Datos: ventas por asesor, leads por asesor.
- Nota: cuantificar como brecha contra el mejor asesor, no contra un benchmark externo.

**F-10 · La base antigua está dormida**
`modulo: reactivacion` · `etapa: post_perdida` · **~5/53**
- Síntoma: "antes hacíamos segmentación y ya no", broadcast semanal sin
  segmentar, base comprada sin trabajar.
- Causa: sin segmentación no hay campaña posible; el envío masivo se degrada.
- Fórmula: `tamaño_base × tasa_reactivacion × conversion_reactivado × margen_por_cliente`
- Datos: tamaño y edad de la base, segmentación disponible.
- Nota: **subdetectada.** El guión tiene un bloque completo y solo aparece en 5
  de 53. Probable falla de captura, no ausencia real.

**F-11 · El cliente que ya compró no vuelve a ser contactado**
`modulo: referidos_fidelizacion` · `etapa: post_venta` · **~4/53**
- Síntoma: "el postventa lo hace un asesor manualmente", "no tenemos
  automatizaciones de postventa, cumpleaños o descuentos".
- Causa: el proceso termina en el cierre.
- Fórmula: `clientes_activos × tasa_recompra_incremental × ticket × margen`
- Datos: clientes activos, recompra actual, duración promedio.

**F-12 · Las renovaciones obligatorias se vencen sin avisar**
`modulo: referidos_fidelizacion` · `etapa: post_venta` · **~2/53**
- Síntoma: "se pierden las renovaciones obligatorias cada 6 meses".
- Causa: la fecha vive en una planilla, no dispara nada.
- Fórmula: `renovaciones_periodo × %_vencidas_sin_contacto × ticket × margen`
- `aplica_si`: existe línea recurrente o documentación con vencimiento.

**F-13 · La pauta trae leads descalificados**
`modulo: atraccion_presencia` · `etapa: captacion` · **~3/53**
- Síntoma: "campañas trajeron datos falsos, perdimos tiempo y presupuesto".
- Causa: sin filtro previo ni scoring, el costo se paga en tiempo del asesor.
- Fórmula: `ad_spend × %_leads_descalificados` + `horas_asesor_perdidas × costo_hora`
- Datos: ad spend, % descalificados, costo del equipo.

**F-14 · El inventario sin precio genera consultas que nadie puede responder**
`modulo: gestion` · `etapa: primer_contacto` · **1/53 (piloto)**
- Síntoma: "el asesor tiene que ir a los semáforos internos y dar un precio
  estimado"; el ítem se publica sin precio para justificar el costo de tasarlo.
- Causa: catálogo incompleto por diseño del negocio.
- Cierre parcial: exponer la fuente interna de precios al bot, o responder con
  el proceso ("pendiente de avalúo; si estás interesado, formalicemos") en vez
  del precio.
- Fórmula: `consultas_sin_precio_mes × tiempo_asesor × costo_hora`
- `aplica_si`: `linea.estado_del_catalogo.items_publicados_sin_precio`

**F-15 · El proceso depende de un tercero que controla el activo**
`modulo: gestion` · `etapa: agendamiento` · **1/53 (piloto)** ·
`cerrable_por_ropofy: false`
- Síntoma: ciclo de agendamiento de 7–10 días (lotes semanales de solicitud de
  llaves) en un mercado donde el interesado ya está viendo cinco competidores.
- Causa: el tercero controla llaves, disponibilidad y alistamiento.
- **Solo mitigable**: automatizar la solicitud (correo disparado por el CRM en
  el momento, no en lote) y medir el ciclo para negociarlo con datos.
- Fórmula del costo (para visibilizar, no para prometer):
  `visitas_solicitadas × %_perdido_por_espera × conversion_visita × margen`
- `aplica_si`: `linea.control_del_activo == tercero_institucional` o existe
  `dependencias_externas_del_proceso` en la etapa.

**F-16 · El lead ya calificado no se distingue del curioso**
`modulo: gestion` · `etapa: primer_contacto` · **1/53 (piloto)**
- Síntoma: quien completó el registro y aprobó el filtro de cumplimiento escribe
  por el mismo canal que el curioso, y el asesor no lo sabe "a menos de que él
  diga: yo ya me registré".
- Causa: el dato de calificación **ya existe** en otro sistema del cliente y no
  está a la vista del canal.
- Distinta de F-13: allá el lead es basura; acá el lead es oro tratado como basura.
- Cierre: integración con la plataforma del cliente + `scoring` de contacto.
- Fórmula: `leads_calificados_mes × delta_conversion_por_prioridad × margen`
- `aplica_si`: existe `plataforma_propia` con registro o precalificación.

**F-17 · Se descalifican leads en masa para cumplir un indicador externo**
`modulo: gestion` · `etapa: transversal` · **1/53 (piloto)** ·
`cerrable_por_ropofy: false`
- Síntoma: cartas de desistimiento enviadas en masa "para poder salir de esos
  clientes, porque mis indicadores no daban".
- Causa: un indicador impuesto por el tercero castiga leads no cerrados; la
  organización destruye pipeline deliberadamente para que la razón cuadre.
- **Solo mitigable**: medir la calidad real del lead recibido (scoring +
  atribución) para renegociar el indicador con evidencia. La tecnología no
  arregla el incentivo; lo documenta.
- `aplica_si`: existe `indicadores_impuestos_externamente` que penaliza volumen
  no cerrado.

**F-18 · La llamada perdida no se devuelve**
`modulo: gestion` · `etapa: entrada` · **caso AYC + patrón de sector**
- Síntoma: línea fija y celular publicados en avisos, vitrinas y portales;
  cuando el equipo está saturado o fuera de horario nadie contesta y **nadie
  sabe que esa llamada existió**. "La telefonía está en un punto crítico: muchas
  líneas y ninguna métrica de llamadas perdidas o efectivas."
- Causa: el canal de voz vive fuera del CRM. Un mensaje no contestado queda
  visible en la bandeja; una llamada perdida no deja rastro en ningún lado.
- Distinta de F-02 (fuera de horario en texto): aquí el contacto no deja huella
  escrita, así que la fuga es invisible incluso para quien la sufre.
- Cierre: numeración en el CRM + rescate automático (mensaje inmediato + tarea).
- Fórmula: `llamadas_perdidas_mes × tasa_rescate × conversion_lead_telefonico ×
  margen`. **Cuidado**: en modo A exige el dato de llamadas perdidas, que casi
  nunca existe antes de implementar — por eso normalmente se presenta en volumen
  y se cuantifica después, con el propio tablero.
- `aplica_si`: existe número telefónico publicado como canal de entrada.

**F-19 · El pedido de ciclo corto vive en la cabeza de quien lo tomó**
`modulo: cierre` · `etapa: cierre` · **caso Bifteki (primer negocio de ciclo corto)**
- Síntoma: el pedido se toma por WhatsApp y se le grita a la cocina. Nadie puede
  decir en qué va sin preguntarle a alguien; el cliente vuelve a escribir «¿ya
  salió?» y la respuesta depende de que alguien se acuerde. Pedidos que se caen
  entre el chat y el sector de preparación, y reclamos que llegan antes que el
  pedido.
- Causa: en el ciclo corto no hay artefacto. Sin cotización ni contrato, el
  pedido nunca se vuelve un objeto del sistema: no tiene estado, ni dueño, ni
  reloj. Los nueve componentes de cierre formal asumían el artefacto y por eso
  este negocio se quedaba sin módulo.
- Distinta de **F-08** (el volumen desborda la capacidad): aquí el volumen puede
  ser perfectamente manejable y el pedido igual se pierde, porque lo que falta es
  el registro, no la capacidad. Distinta de **F-15**: el tramo que se pierde es
  el propio, no el del tercero que reparte.
- Cierre: pipeline de pedido con etapas y SLA en minutos — el pedido se vuelve
  objeto con estado. Mitigan la confirmación al cliente, el despacho por sector y
  la alerta de estancamiento.
- Fórmula: `pedidos_mes × %_con_incidencia × ticket_promedio × margen`
- Datos: pedidos por mes, % con reclamo o reproceso, ticket promedio.
- `aplica_si`: `linea.ciclo_dias == 0 and linea.mecanismo_de_cierre == venta_directa`

---

### Fugas del embudo oferente

Cuando `linea.sujeto_del_embudo == oferente`, el lead es quien ofrece el activo
(propietario, consignatario). Ninguna fuga F-01 a F-17 aplica tal cual.
**Derivadas de un solo caso (piloto) — validar contra más diagnósticos.**

**FO-01 · La precaptación en campo no entra al sistema**
`modulo: gestion` · `sujeto: oferente`
- Síntoma: recorridos de calle anotando letreros de "se vende"; los datos viven
  en las notas del ejecutivo hasta que él decide contactar.
- Causa: no hay captura móvil ni pipeline de precaptación.
- Cierre: formulario móvil + pipeline propio con etapas
  precaptación → contacto → visita de estimación → contrato.
- Fórmula: `precaptaciones_mes × %_nunca_contactadas × valor_captacion × margen`

**FO-02 · El propietario contactado una vez no se retoma**
`modulo: nutricion` · `sujeto: oferente`
- Síntoma: el propietario que dijo "ahora no" desaparece; nadie lo recontacta
  cuando el inmueble sigue publicado meses después.
- Causa: la nutrición existente (si existe) habla en lenguaje de comprador.
- Cierre: secuencia específica de oferente (señales: sigue publicado, bajó de
  precio, cambió de inmobiliaria).
- Fórmula: `contactos_oferentes_mes × %_sin_retoma × tasa_conversion_captacion × valor_captacion`

**FO-03 · La exclusiva se pierde contra la inmobiliaria que respondió primero**
`modulo: gestion` · `sujeto: oferente`
- Síntoma: el propietario interesado que llega por la web espera respuesta
  mientras otras inmobiliarias con las que también habló ya lo visitaron.
- Causa: los leads oferentes entran por el mismo canal que los demandantes, sin
  prioridad ni ruteo a la función captadora.
- Cierre: ruteo por intención (comprar vs. consignar) desde el primer mensaje.
- Fórmula: `leads_oferentes_mes × %_perdidos_por_demora × valor_captacion × margen`

---

### Categoría: ceguera

**C-01 · No se sabe cuántos leads convierten ni dónde se pierden**
`modulo: tableros` · **~22/53**
- Síntoma: "para saber las oportunidades abiertas hay que revisar chat por chat";
  "no sé cuántos leads entran"; reportes generados a mano.
- Cuantificación: **no se monetiza como pérdida.** Se cuantifica como
  `ad_spend_mensual + costo_equipo_comercial` operando sin evaluación posible.
- Nota: esta es la ceguera madre. Su presencia degrada la confianza de todas las
  demás cifras del diagnóstico, y eso debe declararse en la propuesta.

**C-02 · No se puede atribuir la venta a un canal**
`modulo: tableros` · **~5/53**
- Síntoma: "todo queda como WhatsApp, sin saber si vino de Meta o Google".
- Cuantificación: `ad_spend_mensual` sin ROAS calculable.
- Nota: bloquea el cálculo de CAC de pauta del guión. Si esta ceguera está
  presente, el CAC reportado es estimado y hay que decirlo.

**C-03 · Los datos viven en cuatro lugares distintos**
`modulo: gestion` · **~25/53**
- Síntoma: WhatsApp + Excel + cuaderno + ERP; contactos en el teléfono personal.
- Cuantificación: no directa. Es **causa raíz** de C-01 y de F-01 a F-09.
- Nota: es el dolor más frecuente del set junto con F-01, y casi nunca es la
  fuga que hay que vender — es el prerrequisito que las habilita a todas.

**C-04 · Las llamadas y los mensajes se cuentan a mano**
`modulo: gestion` · **caso AYC, sospecha de alta frecuencia**
- Síntoma: alguien lleva la cuenta en una libreta o Excel y el viernes se
  reporta en comité: "tuvimos 300 llamadas, 400 WhatsApps". La gerente de AYC lo
  llamó "la era del ábaco" y calculó su conversión (1%) mentalmente en la
  sesión.
- Cuantificación: no directa. Es la **ceguera del canal de voz** — hermana de
  C-01 y prerrequisito de todo cálculo de CAC por canal.
- Nota de venta: cuando el cliente ya cuenta a mano, no hay que convencerlo del
  valor de medir — ya lo cree, y está pagando el costo en horas de alguien. El
  argumento es el reemplazo del ábaco, no la introducción de la métrica.
- Cierre: `gestion-telefonia` (registro automático) + tableros.

---

### Categoría: restriccion

| id | Restricción | Frecuencia | Implicación |
|---|---|---|---|
| R-01 | Ventana de 24 h de WhatsApp limita el seguimiento | ~4/53 | Requiere plantillas aprobadas por Meta |
| R-08 | Las llamadas salientes por WhatsApp exigen permiso del contacto | nueva | Permiso temporal (7 días) o permanente, revocable por el usuario. Topes: 1 solicitud/contacto cada 24 h, máx. 2 en 7 días, 100 llamadas conectadas por número cada 24 h. **4 llamadas seguidas sin contestar → Meta revoca el permiso.** Se vende como "llamamos a quien nos autorizó", nunca como marcación libre |
| R-09 | La coexistencia bloquea las llamadas por WhatsApp | nueva | Si el número sigue en la app de WhatsApp Business (app + API a la vez), el canal de voz no se habilita. Decisión previa a la propuesta: ver "el triángulo del número" en modulo-gestion §E |
| R-02 | Bloqueos por envío masivo desde WhatsApp Business | ~4/53 | Requiere API oficial, no QR |
| R-03 | Conexión por QR se cae o arriesga el número | ~3/53 | Prerrequisito de API |
| R-04 | Migración de línea a API con pérdida de historial | ~3/53 | Expectativa a gestionar antes de vender |
| R-05 | Aprobación de plantillas Meta demora | ~2/53 | Afecta cronograma, no alcance |
| R-06 | Integración con core propio (ERP, DMS, historia clínica) | ~6/53 | Puede requerir n8n o API directa |
| R-07 | Conectividad deficiente en la zona del cliente | ~1/53 | Riesgo de adopción |

Las restricciones no se cuantifican. Se declaran como prerrequisitos y alimentan
`prerequisito_plataforma` de los componentes.

---

### Categoría: objecion

| id | Objeción | Frecuencia |
|---|---|---|
| O-01 | Desconfianza en que la IA responda bien o suene robótica | ~6/53 |
| O-02 | Mala experiencia previa: proveedor que no implementó lo prometido | ~5/53 |
| O-03 | Miedo al modelo de cobro por conversación o por volumen | ~3/53 |
| O-04 | Falta de capacidad técnica interna para operar la herramienta | ~4/53 |
| O-05 | Migración previa mal hecha con pérdida de historial | ~2/53 |

Nunca generan componentes. Alimentan la narrativa de la propuesta y el
argumento de acompañamiento. O-02 y O-04 juntas aparecen en casi 1 de cada 5
casos: el diferencial no es el software.

Nota de gobernanza (aprendizaje AYC): una variante específica de O-02 en
inmobiliarias — notificaciones automáticas a propietarios desactivadas porque
los asesores escribieron comentarios inadecuados. Regla derivada para
Fidelización y Reputación: toda comunicación automática hacia propietarios sale
de **plantilla controlada, nunca texto libre del asesor**. Preguntar por esta
experiencia previa antes de proponer notificaciones a propietarios.

---

### Categoría: carencia_demanda

| id | Carencia | Frecuencia |
|---|---|---|
| D-01 | No hacen marketing digital ni tienen tráfico propio | ~8/53 |
| D-02 | No tienen web, o es un landing sin formulario | ~5/53 |
| D-03 | Sin inventario o cartera que ofrecer | ~2/53 |
| D-04 | Base de datos inexistente (negocio nuevo) | ~3/53 |

Cuando D-01 o D-02 dominan, **las fugas de conversión son secundarias**: no hay
volumen que fugarse. Vender Nutrición o Reactivación a un cliente con D-04 es
vender capacidad ociosa. Esto debe ser una regla de la etapa 3, no un criterio
del consultor.

---

### Categoría: friccion_propia

| id | Fricción | Frecuencia |
|---|---|---|
| FP-01 | Registro propio desproporcionado para la intención del usuario (14 pasos para preguntar) | 1/53 (piloto) |

Se documenta con evidencia (capturas, conteo de pasos, comparación con el
estándar del mercado) y se entrega como recomendación al cliente. No genera
componentes. **Regla de medición**: mientras la fricción exista, toda tasa de
conversión aguas abajo está contaminada por ella, y los tableros deben anotarlo.

---

## 4. Regla anti-doble-conteo

Un mismo lead perdido aparece en F-02, F-03, F-06, F-08 y termina en F-10. Si se
suman todas, se promete recuperar más de lo que existe.

**Regla:** cada fuga se cuantifica contra el volumen de **su** etapa de embudo,
y el total recuperable del plan se topa así:

```
recuperable_total ≤ (leads_mes − clientes_nuevos_mes) × techo_recuperacion × margen
```

`techo_recuperacion` es un parámetro conservador único de Ropofy, no una
estimación por caso. Dentro del tope, las fugas se ordenan por severidad y se
reporta la de mayor impacto individual — no la suma.

En la propuesta se presenta **la fuga dominante cuantificada** y las demás como
concurrentes, sin sumar cifras.

---

## 5. Cuantificación, compromiso y caso de éxito

Tres afirmaciones distintas que la propuesta nunca debe mezclar:

**1. La fuga (presente, con datos del cliente).** "Hoy quedan ~40 propuestas al
mes sin retomar; a tu ticket son $X." Es descripción, no promesa. Rigor total
aquí: fórmula del catálogo, datos con fuente y periodo.

**2. La proyección (futuro, en escenarios).** Siempre rango conservador /
esperado, nunca un punto. Topada por `techo_recuperacion` (§4). Se presenta como
escenario, jamás como compromiso contractual.

**3. El compromiso (lo que Ropofy controla).** Solo indicadores adelantados:
tiempo de primera respuesta, % de leads con seguimiento activo, % de citas
confirmadas, % de propuestas con secuencia de retoma, cobertura de reactivación.
Nunca ventas, ingresos ni conversión final — eso depende del equipo, el precio y
el mercado del cliente. Cada compromiso debe corresponder a una
`metrica_que_habilita` de un componente del plan vendido: no se compromete lo
que no se va a poder medir.

### Los dos modos de la propuesta

El modo lo decide `datos_economicos_capturados` de la ficha, no el consultor:

| | Modo A — con datos | Modo B — sin datos |
|---|---|---|
| Fugas | Cuantificadas en dinero, con fórmula visible | En volumen y proceso ("~4.000 conversaciones sin atender") |
| Proyección | Escenarios conservador/esperado | No se proyecta |
| Cierre | Decisión sobre cifras | Incluye la solicitud de los datos faltantes como paso del cierre — es el motivo natural de la siguiente reunión |
| Declaración | Fuente y periodo de cada cifra | Línea explícita: "la cuantificación económica requiere estos N datos" |

Un modo B que aparenta ser modo A —cifras inventadas o benchmarks disfrazados de
datos del cliente— es el peor resultado posible: compromete el caso de éxito
futuro con una línea base falsa.

### El caso de éxito es el subproducto

- **Antes**: el formulario de datos duros del guión, con fuente y periodo,
  archivado con el diagnóstico. Es la línea base.
- **Después**: los tableros del plan implementado miden exactamente las
  `metrica_que_habilita` de los componentes vendidos.
- **Regla de diseño**: toda fuga cuantificada en la propuesta debe tener su
  métrica de seguimiento en un tablero del plan. Si se vendió la fuga, se debe
  poder medir su evolución — eso es lo que convierte cada implementación en un
  caso de éxito con datos duros a los 6 meses, sin esfuerzo adicional de nadie.

---

## 6. Hallazgos que exigen decisión

**Referidos y Reputación: cero menciones en 264 dolores.** Ningún cliente en 53
diagnósticos mencionó reseñas ni referidos como problema. No es solo falta de
intake — no se percibe como dolor. Consecuencias:
- No se pueden vender desde la sección de fugas.
- Probablemente no pertenecen a Fundamental.
- Necesitan narrativa de oportunidad, con su propia forma de cuantificación
  (por ejemplo, % de ventas que hoy ya llegan por referido espontáneo, dato que
  el Bloque 1 del guión sí captura).

**F-10 está subdetectada.** El guión dedica un bloque completo a reactivación y
solo aparece en 5 de 53 casos. Al reprocesar los diagnósticos, verificar si el
dato de tamaño de base estaba presente y no se registró como dolor.

**C-03 es causa, no fuga.** Aparece en ~25 casos, tantos como F-01, pero
venderla como fuga es un error: centralizar no recupera dinero por sí solo.
Recupera dinero porque habilita F-01 a F-09. En el lienzo debe verse como
cimiento, no como pieza de retorno.

**El silencio en los dolores es señal de madurez, no de irrelevancia.** Que
Referidos y Reputación tengan cero menciones en 264 dolores no significa que no
importen — significa que **el cliente promedio no ha llegado a la etapa donde
duelen**. Nadie sufre por no tener programa de referidos cuando pierde el 60% de
sus leads por falta de respuesta. Esto convierte la escalera de planes en una
escalera de madurez: Fundamental resuelve lo que duele hoy; Avanzado e
Inteligente resuelven lo que va a doler cuando lo de hoy esté resuelto. Dos
consecuencias prácticas: (a) los módulos silenciosos pertenecen a planes
superiores por madurez, no solo por empaquetado — decisión aplicada: Referidos,
Reputación y Reactivación arrancan en Avanzado; (b) su argumento de venta no es
la fuga actual sino la siguiente etapa: "cuando dejes de perder leads, tu
problema será que no vuelven ni te refieren — y ese plan ya lo trae resuelto".

**Falta el diccionario de métricas.** Las fórmulas de este catálogo referencian
`conversion_base`, `margen_por_cliente`, `capacidad_mensual_equipo` y otros que
todavía no tienen definición única. Sin eso, dos consultores cuantifican la
misma fuga distinto.

**Las fugas F-14 a F-17, FO-01 a FO-03 y FP-01 provienen de un solo caso.**
Están en el catálogo porque el mecanismo es generalizable (catálogo sin precio,
tercero que controla el activo, calificación invisible, indicador externo
perverso, embudo oferente), pero su frecuencia real se conocerá al reprocesar
los 53 diagnósticos con la ficha v0.2.

**Sin datos económicos no hay cuantificación — y hay que decirlo.** El piloto
demostró que una sesión de 90 minutos puede mapear el proceso completo sin
capturar un solo dato económico. Cuando eso pasa, la propuesta corre en modo B
(§5) y la solicitud de datos se vuelve parte del cierre.
