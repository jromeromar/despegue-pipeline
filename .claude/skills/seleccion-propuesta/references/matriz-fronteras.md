# Matriz de fronteras entre planes — contrato v1.1

Define la identidad de cada plan, su frase, su prueba de pertenencia y las
habilidades de IA que desbloquea. Es el documento que responde "¿por qué este
componente está en este plan?" sin discutir caso por caso.

---

## 1. La escalera (léase de abajo hacia arriba)

| | Fundamental | Avanzado | Inteligente |
|---|---|---|---|
| **Frase** | **Nada se pierde.** Cada conversación con dueño, origen y tarea — el caos se vuelve orden. | **El sistema trabaja.** Atiende, agenda, confirma, firma y despierta tu base — mientras tu equipo vende. | **El sistema persigue y decide.** Ningún lead se enfría: retoma solo, prioriza solo, recomienda solo y habla en cifras. |
| **Qué compra el cliente** | Orden y visibilidad | Automatización del presente | Persecución automática del futuro |
| **El sistema actúa…** | cuando alguien del equipo actúa | cuando el cliente final actúa | **cuando nadie actúa** |
| **Metáfora** | el archivo deja de perderse | la recepción nunca duerme | el vendedor que nunca olvida |

**La prueba de pertenencia** (para clasificar cualquier componente nuevo):

- ¿Registra, ordena, enruta o hace visible? → **Fundamental**
- ¿Responde o ejecuta cuando el cliente final hace algo (escribe, agenda, firma, responde una campaña)? → **Avanzado**
- ¿Actúa cuando NO pasa nada — silencio, enfriamiento, tiempo transcurrido, coincidencia de catálogo, umbral de score? → **Inteligente**

Esa es la línea que las correcciones de agosto-2026 dejaron limpia: las
secuencias de retoma, el goteo de email y las alertas de coincidencia son
Inteligente porque **se disparan por ausencia de acción**, no por acción.

---

## 2. Qué desbloquea cada salto (argumento de venta)

### Fundamental → Avanzado: "deje de contestar usted"
El equipo deja de ser el cuello de botella del presente: el asistente atiende y
agenda, las citas se confirman solas, los contratos se firman en línea, la base
dormida se despierta por oleadas.

### Avanzado → Inteligente: "deje de perseguir usted"
Todo lo que en Avanzado muere si nadie lo retoma, en Inteligente se retoma solo:

- **La cotización en visto** → secuencia de propuesta la persigue.
- **El lead que dejó de responder** → secuencia de no-respuesta insiste con método.
- **El propietario que dijo "ahora no"** → secuencia de oferente vuelve con razones.
- **El lead de decisión lenta** → goteo de email lo madura semanas.
- **El inmueble nuevo que le sirve a alguien** → alerta de coincidencia le avisa primero.
- **El que está por decidir o por irse** → señales de decisión y de riesgo lo delatan.
- **La fila de atención** → el score la ordena por valor, no por orden de llegada.
- **La llamada de las 9 pm** → la contesta la IA de voz.
- **El número del negocio** → tablero económico: el sistema habla en pesos.

La línea de cierre del consultor: *"Avanzado trabaja mientras su equipo vende.
Inteligente vende mientras su equipo duerme."*

---

## 3. Habilidades del asistente de IA por plan

El nivel lo fija el plan (N1/N2/N3), y además **la habilidad misma tiene plan de
entrada** — esto es lo que hace al asistente de Inteligente otro producto, no el
mismo bot con más profundidad:

La fuente de verdad de las habilidades es
`catalogo-habilidades-ia.md` (contrato v1.1): alcance, fuera_de_alcance y
niveles viven allí. Esta tabla es su matriz consolidada por plan.

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
asistente** (regla de lenguaje del catálogo §0): el argumento del salto a
Avanzado ("deje de contestar usted") queda intacto porque N1 responde pero no
ejecuta. La familia transaccional (Vendedor Virtual, catálogo §3.12) no aparece
en esta matriz a propósito: es producto aparte, no plan.

---

## 4. Cuotas por plan (lo que se puede pedir sin renegociar)

| Cuota | Fundamental | Avanzado | Inteligente |
|---|---|---|---|
| Formularios embebibles | 3 | 5 | 8 |
| Agendas/calendarios | 3 | 5 | 10 |
| Campañas de reactivación | — | 2 | 4 + ciclo permanente |
| Piezas de conocimiento que Ropofy redacta | 10 | 25 | 50 |
| Plantillas de WhatsApp gestionadas | 4 | 8 | 15 |
| Reglas de asignación | 3 | 6 | ilimitadas dentro de la librería |
| Rondas de entrenamiento inicial del asistente | *por confirmar* | *por confirmar* | *por confirmar* |
| Ajustes del asistente post-activación, por mes | *por confirmar* | *por confirmar* | *por confirmar* |

**Las dos últimas cuotas están sin fijar** (catálogo de habilidades §4). El
brochure ago-2026 traía 4/6 rondas de entrenamiento y 4/6/8 ajustes mensuales,
pero esas cifras eran **por bot standalone**; al replegarse los bots a los
planes hay que fijarlas por plan, y esa decisión es de producto. Se registran
aquí para que no se pierdan, no para usarse. Ambas cuentan **entregables, no
horas** — consistentes con la decisión "sin boosters ni bolsas de horas".

(Recordatorio de la regla global del copy: Ropofy redacta el punto de partida
con metodología; el texto final lo proporciona o aprueba el cliente.)

---

## 5. Silencios que esta matriz explica

- Fundamental **incluye respuesta inmediata (N1): responde, no ejecuta. No se
  comercializa como asistente** — esa palabra y ese argumento pertenecen a
  Avanzado.
- Reactivación **empieza en Avanzado** (oleadas) y solo se vuelve **permanente
  en Inteligente**: despertar una base exige que Gestión ya esté operativa.
- El **tablero económico es Inteligente** aunque técnicamente sea simple: sin
  datos económicos del cliente no funciona, y pedirlos es una conversación de
  madurez, no de configuración.
