# Schema del componente tipado — Librería de módulos Ropofy

Contrato de datos v0.2 (actualizado con el piloto Activos por Colombia).
Cada pieza implementable del catálogo es un **componente**.
El catálogo completo es el alcance del plan Inteligente.

---

## 0. Decisión previa: reconciliar taxonomías

Hoy existen dos mapas en paralelo:

| Público (ropofy.com) | Interno (módulos) |
|---|---|
| Atrae | Atracción — Presencia |
| — | Atracción — Reputación *(público: bajo Fideliza)* |
| Gestiona | Gestión |
| Nutre | Nutrición |
| — | Reactivación *(público: dentro de Nutre)* |
| Cierra | Cierre |
| Fideliza | Referidos y Fidelización |
| — | Tableros y Reportes *(público: repartido en 3 secciones)* |

El campo `modulo` usa la taxonomía interna de 7. El lienzo que ve el cliente
debe mostrar la interna, y el sitio debería alinearse a ella. No mantener dos.

---

## 1. Campos comunes (todos los componentes)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | slug | Estable para siempre. Las dependencias apuntan aquí. |
| `nombre_interno` | texto | Lenguaje técnico, para el equipo de implementación. |
| `nombre_cliente` | texto | Lenguaje de negocio. Es el que se renderiza en el lienzo. |
| `modulo` | enum(7) | atraccion_presencia · atraccion_reputacion · gestion · nutricion · cierre · reactivacion · referidos_fidelizacion · tableros |
| `tipo` | enum | Primitiva de plataforma. Determina el schema de `detalle`. Ver §2. |
| `posicion_journey` | entero | Orden dentro del recorrido. El **tramo** (la fila del lienzo) se deriva de este número, no se declara aparte — ver §1.1. |
| `visibilidad_cliente` | enum | `front` (lo percibe el cliente final del cliente) · `back` (herramienta interna del equipo) · `ambos` (una cara para cada uno). Obligatorio. Se pinta como etiqueta en el lienzo. (v0.2.7, origen: la pregunta de AYC "¿esos recordatorios son para el cliente o para nosotros?" destapó que la propuesta no tenía los internos.) |
| `plan_minimo` | enum | fundamental · avanzado · inteligente. Acumulativo. |
| `mecanismo_entrega` | enum | snapshot · configuracion_cuenta · integracion_externa · contenido_a_medida · capacitacion. **Regla global del copy** (aplica a todo `contenido_a_medida`: saludos, plantillas, emails, lead magnets, piezas de nutrición): Ropofy entrega un punto de partida con metodología recomendada; el texto final lo **proporciona o aprueba el cliente** antes de activarse. La voz de la marca es del cliente; la estructura y el método son de Ropofy. La propuesta debe decirlo. |
| `se_instancia_por` | [enum] | **Lista, no valor único.** unico · linea_negocio · sujeto_del_embudo · funcion · territorio · control_del_activo. Un pipeline puede instanciarse por línea × sujeto. |
| `aplica_si` | expresión | Condición sobre la ficha de perfil. Vacío = siempre aplica. Puede referenciar `control_del_activo` — la condición que decide si el agendamiento es automatizable. |
| `bloqueado_por_tercero` | expresión | Condición bajo la cual el componente NO es implementable por depender de un sistema fuera del control del cliente (ej: sincronización con el tercero institucional). Si evalúa verdadero para un perfil, el componente se excluye o degrada, y la propuesta lo declara. |
| `depende_de` | [id] | Referencias, nunca texto libre. |
| `integraciones_requeridas` | [id] | Del registro de integraciones. |
| `cierra_fugas` | [id_fuga] | El componente elimina la causa de la fuga. |
| `mitiga_fugas` | [id_fuga] | El componente reduce o hace visible una fuga cuya causa no controla el cliente. Nunca se promete cierre sobre estas. |
| `metrica_que_habilita` | [slug] | Qué se vuelve medible al implementarlo. Alimenta Tableros. |
| `esfuerzo_base` | puntos | Costo de la primera instancia. |
| `esfuerzo_por_instancia` | puntos | Costo de cada instancia adicional. 0 si `unico`. |
| `costo_externo` | objeto | Qué se paga además de la implementación. `{ tipo, detalle, quien_paga }` con tipo: `incluido` (nada extra) · `consumo_variable` (se paga por uso: conversaciones de WhatsApp, minutos de voz, uso de IA) · `licencia_del_cliente` (requiere una suscripción o API que el cliente contrata y paga: su ERP, su pasarela, su portal) · `desarrollo_a_cotizar` (integración no estándar, se cotiza aparte tras evaluación técnica). **Obligatorio en `tipo: integracion` y `tipo: telefonia`.** Vacío equivale a `incluido`. (v0.2.6: sin este campo la propuesta deja creer que todo lo dibujado está pagado.) |
| `prerequisito_plataforma` | [texto] | Ej: plan Unlimited, WhatsApp API aprobada, A2P registrado. |
| `cuotas_por_plan` | mapa | El mismo componente con parámetros distintos por plan, en lenguaje "hasta N". Ej: campañas de reactivación `{avanzado: 2, inteligente: 4}`; calendarios `{avanzado: 5, inteligente: 10}`; reglas de asignación `{fundamental: 1, avanzado: 3, inteligente: 3}`. Vacío = el componente no escala por cantidad. (v0.2.3, aprendizaje AYC: los planes se diferencian por cantidad, no solo por pertenencia.) |
| `unidad_de_cuota` | texto | Qué cuenta la cuota: campañas, calendarios, reglas, landings, follow-ups. |
| `detalle` | objeto tipado | Según `tipo`. Ver §2. |

### Notas de diseño

**`plan_minimo` y `aplica_si` son ortogonales.** Un componente puede ser
Fundamental y no aplicar a un cliente. Plan = qué compró. `aplica_si` = qué
tiene sentido para su estructura. No colapsarlos.

**`mecanismo_entrega` es el predictor real de esfuerzo.** Un snapshot se
despliega en minutos; una integración externa requiere credenciales, pruebas y
a veces aprobación de terceros. Lo que no viaja en snapshot: contactos,
conversaciones, credenciales de integración, LC Phone, registro A2P, usuarios y
permisos, datos de reputación, dominios.

**Dos nombres, no uno.** `nombre_interno` = "Workflow speed-to-lead con
reasignación por SLA". `nombre_cliente` = "Respuesta automática en menos de un
minuto". El lienzo usa el segundo; el spec BPMN usa el primero.

---

### 1.1 Tramos del recorrido (derivados, no declarados)

El renderizador calcula la fila del lienzo a partir de `posicion_journey`. Nadie
asigna tramo a mano: así un componente nuevo cae solo en su lugar.

| Tramo | Rango | Etiqueta en el lienzo |
|---|---|---|
| 1 · Atrae | 1–9 | Atracción |
| 2 · Gestiona | 10–45 | Gestión |
| 3 · Nutre | 50–66 | Nutrición |
| 3b · Despierta | 90–99 | Reactivación *(sub-tramo: vive dentro de Nutrición, no es etapa nueva)* |
| 4 · Cierra | 70–87 | Cierre |
| 5 · Retiene y refiere | 105–121 | Referidos y Fidelización *(incluye Reputación, journey 105–108, aunque su módulo sea `atraccion_reputacion`)* |
| ✳ Transversal | 130+ | Tableros *(no ocurre en un momento: atraviesa todo)* |

Dos reglas que se derivan de la tabla:

- **`modulo` y tramo no siempre coinciden**, y eso es correcto: Reputación
  pertenece a Atracción por efecto (trae clientes) pero ocurre después del
  cierre. El lienzo la dibuja en el tramo 5 con un lazo de retorno hacia el
  tramo 1. Igual el registro de referidos.
- **Los rangos tienen huecos a propósito** (46–49, 67–69, 88–89, 100–104,
  122–129). Son espacio para componentes futuros sin renumerar la librería.

### 1.2 Reglas de agrupación en el lienzo

Dos casos donde el renderizador **no** dibuja una tarjeta por componente:

- **`tipo: chatbot_ia` → un solo nodo "Asistente IA"** con sus habilidades
  listadas y el nivel que da el plan. Nunca N cajas de bot: cinco cajas se leen
  como cinco robots y activan la objeción más frecuente del sector.
- **`tipo: integracion` y `tipo: telefonia` con `costo_externo` distinto de
  `incluido` → carril lateral de integraciones**, cada una con su etiqueta de
  costo. Así el cliente ve en un solo lugar qué paga aparte.

## 2. Tipos y su `detalle`

### `pipeline`
```
etapas[]: { nombre, criterio_entrada, criterio_salida, sla_dias, es_perdida }
motivos_perdida[]: texto
objeto_base: oportunidad | objeto_personalizado
```

### `campos_personalizados`
```
campos[]: { nombre, tipo, objeto, opciones[], obligatorio, unico, es_para_reporte }
```
`tipo` ∈ texto · numero · moneda · fecha · opcion_unica · opcion_multiple · archivo · booleano
`objeto` ∈ contacto · oportunidad · empresa · objeto_personalizado
`unico` es irreversible en GHL — marcarlo mal cuesta rehacer el objeto.

### `objeto_personalizado`
```
nombre_objeto, nombre_plural
campos[]: { igual que campos_personalizados }
asociaciones[]: { con_objeto, cardinalidad, etiqueta }
```
`cardinalidad` ∈ uno_a_muchos · muchos_a_muchos. Tope: **10 objetos por subcuenta.**

### `automatizacion`
```
disparador: { tipo, condicion, filtros[] }
acciones[]: { orden, tipo, canal, plantilla_ref, espera_min, asigna_a_funcion }
condiciones_salida[]
ramas[]: { condicion, acciones[] }
```

### `plantilla_mensaje`
```
canal: whatsapp | email | sms | llamada
proposito, variables[], tono
requiere_aprobacion_meta: bool
```
Si `requiere_aprobacion_meta`, debe depender del componente de WhatsApp API.

### `formulario` / `encuesta`
```
campos[]: { etiqueta, campo_destino, obligatorio }
destino: { pipeline_ref, etapa }
accion_post_envio: automatizacion_ref
```

### `calendario`
```
modalidad: individual | round_robin | colectivo
duracion_min, buffer_min, ventana_reserva
asignacion_por: funcion | territorio | linea_negocio
recordatorios[]: { canal, anticipacion }
```

### `embudo_web`
```
paginas[]: { nombre, objetivo, elementos[] }
metrica_conversion
```

### `segmento`
```
mecanismo: tag | smart_list | campo_calculado
criterios[]
uso: [automatizacion_ref | tablero_ref]
```

### `tablero`
```
audiencia_funcion: [funcion]
widgets[]: { metrica, fuente, filtro, visualizacion }
frecuencia_revision
```
Cada `metrica` debe existir como `metrica_que_habilita` de otro componente
presente en el mismo plan o inferior. Ver regla V3.

### `chatbot_ia`
```
habilidad: UNA sola del catálogo canónico (ver catalogo-habilidades-ia.md)
profundidad: 1 | 2 | 3
alcance[]: lo que esta habilidad SÍ hace
fuera_de_alcance[]: lo que esta habilidad NO hace, en lenguaje del cliente
base_conocimiento[]: fuentes (y quién las entrega)
cuotas: { intenciones?, piezas_de_conocimiento_redactadas_por_ropofy?, idiomas? }
criterio_escalamiento
handoff_a_funcion
horario_activo
```
**Un componente = una habilidad.** Nunca "el bot": los asistentes tienen
**amplitud** (cuántas habilidades) y **profundidad** (qué tan lejos llega cada
una), y mezclar las dos dimensiones en un solo ítem de propuesta es la fuente
histórica de disputas de alcance. Reglas duras:

- `fuera_de_alcance` es **obligatorio** y se imprime en la propuesta. Un
  recepcionista que no agenda debe decir "no agenda"; si no lo dice, el cliente
  asume que sí.
- `profundidad` **la fija el plan**, no se cotiza aparte: Fundamental → N1,
  Avanzado → N2, Inteligente → N3. Cada habilidad define qué significa cada nivel
  para ella (ver catálogo). Así el cliente sube de nivel subiendo de plan, y la
  propuesta no necesita una matriz de precios por habilidad × nivel.
- `cuotas` acota lo que el cliente puede pedir sin renegociar. **No se cuenta el
  volumen de preguntas frecuentes** (cargar contenido es barato): se cuenta lo
  que Ropofy tiene que *redactar* cuando el cliente no tiene el material.
- **Regla de render (lienzo)**: todas las habilidades del plan se dibujan como
  **un solo nodo "Asistente IA"** con sus habilidades listadas — el cliente ve un
  asistente, no un ejército de bots. Se venden por separado; se presentan juntas.

(v0.2.5, decisión de producto: los bots se cotizan por habilidad y nivel.)

### `scoring`
```
sujeto: contacto | oportunidad
escala: { min, max }
variables[]: { señal, puntos, fuente_del_dato, es_descalificadora }
umbrales[]: { nombre, min, accion }
```
`fuente_del_dato` es obligatoria: si la señal vive en un sistema externo (registro
en plataforma propia, preaprobación bancaria), el scoring depende de esa
integración y hereda su `bloqueado_por_tercero`.

### `migracion_datos`
```
fuentes[]: { sistema, formato, volumen_estimado }
operaciones[]: deduplicar | normalizar_telefonos | verificar_consentimiento | mapear_campos | etiquetar_origen
destino: { objeto, segmento_ref }
es_recurrente: bool          # una vez (base histórica) o periódica (sistema que sigue vivo)
```
Importación y depuración de bases existentes. La verificación de consentimiento
no es opcional: reactivar una base sin base legal quema la línea y expone al
cliente. (Tipo agregado en v0.2.2, hallazgo del módulo Reactivación.)

### `propuesta_comercial`
```
plantilla_ref, vigencia_dias
datos_requeridos[]: { campo, fuente: crm | catalogo | manual }
seguimiento: { rastrea_apertura: bool, automatizacion_ref }
aceptacion: { mecanismo: aceptacion_en_linea | firma | respuesta_manual, cambia_etapa_a }
```
Cotizaciones y propuestas generadas desde el CRM con historial por contacto.
Distinta de `documento_firmable`: la propuesta se acepta o expira; el documento
se firma. (Tipo agregado en v0.2.1, hallazgo del módulo Cierre.)

### `documento_firmable`
```
proposito, plantilla_ref
datos_requeridos[]: { campo, fuente: conversacion | crm | formulario }
mecanismo_firma: firma_electronica | aceptacion_en_chat
accion_post_firma: { cambia_etapa_a, notifica_a_funcion, automatizacion_ref }
```
Cartas de intención, mandatos, autorizaciones de datos. El valor está en
`accion_post_firma`: la firma mueve el pipeline sin intervención humana.

### `telefonia`
```
proveedor: lc_phone | twilio
numeros[]: { uso: principal | dedicado_por_canal | por_area, canal_origen?, tipo: fijo | movil | toll_free }
enrutamiento: { mecanismo: menu_ivr | round_robin | por_area | directo, destinos_por_funcion[] }
grabacion: { activa: bool, base_legal_declarada: bool, retencion_dias }
registro: { entrantes: bool, salientes: bool, perdidas: bool, duracion: bool }
click_to_call: bool
```
Numeración, enrutamiento, grabación y registro de llamadas dentro del CRM.
**Toda llamada es un evento del contacto**, igual que un mensaje: sin este tipo,
el canal de voz queda fuera del sistema y su atribución y sus fugas son
invisibles. `grabacion.base_legal_declarada` es obligatorio antes de activar —
grabar sin aviso expone al cliente. (Tipo agregado en v0.2.4, hallazgo AYC: la
telefonía es un canal de primera clase que la librería no modelaba.)

### `integracion`
```
sistema, tipo_sistema
direccion: entrada | salida | bidireccional
objetos_sincronizados[]
mecanismo: nativa | webhook | n8n | api_directa
frecuencia, credenciales_requeridas[]
```

### `permisos_usuarios`
```
roles[]: { funcion, alcance_datos, puede_ver_todo, puede_aprobar }
```
`alcance_datos` ∈ propios · equipo · territorio · **externo_afiliado** · todos.
`externo_afiliado`: brokers, aliados o habilitadores que necesitan ver solo el
subconjunto que les corresponde (sus referidos, sus solicitudes de visita).
Este es el componente que traduce jerarquía en configuración.

### `contenido` / `capacitacion`
```
contenido: piezas[]: { tipo, cantidad, quien_produce }
capacitacion: audiencia_funcion[], sesiones, duracion_h, modalidad
```

---

## 3. Reglas de validación del catálogo

Corren sobre la librería, no sobre cada propuesta.

**V1 — Coherencia de planes.** Para todo componente C y toda dependencia D:
`D.plan_minimo <= C.plan_minimo`. Si Fundamental depende de algo que solo
existe en Avanzado, el empaquetado está roto.

**V2 — Cierre de dependencias.** Todo `id` en `depende_de`,
`integraciones_requeridas` y `*_ref` existe en el catálogo.

**V3 — Tableros con fuente.** Todo widget de tipo `tablero` tiene su `metrica`
respaldada por el `metrica_que_habilita` de un componente del mismo plan o
inferior. Sin esto se venden tableros sin datos que los llenen.

**V4 — Cupo de objetos personalizados.** Para un perfil dado, la suma de
instancias de componentes `objeto_personalizado` (aplicando
`se_instancia_por`) no supera 10.

**V5 — Integraciones declaradas.** Si `mecanismo_entrega =
integracion_externa`, entonces `integraciones_requeridas` no está vacío.

**V6 — Cobertura de fugas.** Toda fuga detectada en un diagnóstico termina en
exactamente uno de tres estados dentro de la propuesta: (a) **cerrada** por
componentes del plan recomendado, (b) **mitigada** — componentes que la reducen
o la hacen medible, con la limitación declarada, o (c) **declarada no
abordable** con su causa (tercero que controla el proceso, decisión de negocio
del cliente). Una fuga sin estado es un error de la propuesta; prometer cierre
sobre una fuga solo mitigable también.

**V8 — Implementabilidad.** Ningún componente del plan recomendado tiene
`bloqueado_por_tercero` verdadero para el perfil del cliente. Si lo tiene, se
excluye o se mueve a una fase condicionada, con la condición explícita.

**V11 — Lo no nativo no viaja dentro del plan.** Un componente `tipo: integracion`
cuyo `mecanismo` no sea `nativa` (n8n, API a medida, desarrollo) **no puede tener
`plan_minimo`**: su plan es "ninguno" y su `costo_externo` es
`desarrollo_a_cotizar`. Se dibuja en el carril de integraciones con esa etiqueta
y entra a la orden solo tras evaluación técnica y cotización propia. Razón: el
esfuerzo de una integración a medida depende del sistema del cliente, no de la
librería — incluirla en un plan es prometer un costo que nadie ha medido.
El único compromiso que sí viaja en el plan es la **evaluación técnica** de la
integración (sesión con el proveedor del cliente), que es trabajo acotado.

**V10 — Balance de visibilidad.** En cualquier plan seleccionado, cada módulo
presente aporta al menos un componente `back`. Un módulo que solo trae `front`
automatiza la conversación con el cliente final y no le entrega herramienta al
equipo: es exactamente el hueco que la pregunta de AYC destapó ("¿esos
recordatorios son para el cliente o para nosotros?"). El lienzo puede mostrar el
conteo —*N piezas que su cliente ve · M que su equipo ve*— como chequeo visible
para el consultor y como argumento para el gerente.

**V9 — Fuga vendida, fuga medida.** Toda fuga cuantificada en la propuesta tiene
su métrica de evolución en un tablero del plan recomendado (vía
`metrica_que_habilita`). Esto garantiza la línea base del caso de éxito y hace
verificables los compromisos: solo se compromete lo que un componente del plan
puede medir.

**V7 — Consistencia de journey.** Si dos componentes tienen dependencia,
`posicion_journey` del dependiente es mayor o igual.

---

## 4. Ejemplo — un componente completo

```yaml
id: gestion-pipeline-venta
nombre_interno: "Pipeline de oportunidades con SLA por etapa"
nombre_cliente: "Embudo de ventas visible con alertas de estancamiento"
modulo: gestion
tipo: pipeline
posicion_journey: 30
plan_minimo: fundamental
mecanismo_entrega: snapshot
se_instancia_por: [linea_negocio, sujeto_del_embudo]
aplica_si: "linea.naturaleza in [transaccional, mixta] and linea.sujeto_del_embudo == demandante"
bloqueado_por_tercero: ""
depende_de: [gestion-campos-calificacion]
integraciones_requeridas: []
cierra_fugas: [fuga-sin-visibilidad-embudo, fuga-lead-enfriado]
metrica_que_habilita:
  - conversion_por_etapa
  - dias_en_etapa
  - tasa_cierre_por_asesor
esfuerzo_base: 5
esfuerzo_por_instancia: 3
prerequisito_plataforma: []
detalle:
  objeto_base: oportunidad
  etapas:
    - nombre: "Nuevo"
      criterio_entrada: "Lead creado por formulario, portal o WhatsApp"
      criterio_salida: "Contacto efectivo registrado"
      sla_dias: 1
      es_perdida: false
    - nombre: "Calificado"
      criterio_entrada: "Presupuesto y necesidad confirmados"
      criterio_salida: "Visita o demo agendada"
      sla_dias: 3
      es_perdida: false
  motivos_perdida: ["Sin presupuesto", "Eligió competencia", "No contactable"]
```

---

## 5. Lo que este schema deja pendiente

- **Catálogo de fugas** con `id`, síntoma, causa y fórmula de cuantificación.
  Es el otro lado de `cierra_fugas` y todavía no existe.
- **Registro de integraciones** con `id` por sistema, para que
  `integraciones_requeridas` tenga a qué apuntar.
- **Diccionario de métricas** con `id`, definición y fuente, para que V3 sea
  verificable.
- **Taxonomía de funciones** — definida en la ficha de perfil v0.2 (incluye
  cumplimiento, habilitador_de_activo y externo_afiliado); falta versionarla
  como archivo propio compartido con el spec BPMN.
- **Matriz de fronteras de plan**: la frase que justifica cada salto (enunciada
  en modulo-tableros §D) + cuotas de entregables + precio base. **Decisión de
  producto (ago-2026): sin boosters ni bolsas de horas.** El compromiso es por
  entregable, sin contador de tiempo — los contadores de servicio invitan al
  cliente a microgestionar el cómo en vez de recibir el qué. La línea limpia:
  las cuotas cuentan **lo que el cliente recibe** (campañas, calendarios,
  reglas); nunca cuentan esfuerzo, horas ni sesiones. `esfuerzo_base` y
  `esfuerzo_por_instancia` son internos para cotizar y jamás se exponen en la
  propuesta.
- **Fugas del embudo oferente**: catálogo v0.2 incluye una primera versión
  derivada de un solo caso; validar contra más diagnósticos con líneas de
  captación.
