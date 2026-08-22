# Criterios de evaluación de la ficha — los que exigen juicio

El validador (`scripts/validar_ficha.py`) cubre lo verificable por máquina.
Estos seis criterios exigen leer la transcripción junto a la ficha. Se usan
para auto-revisión antes de entregar y para auditoría humana por muestreo.

## J1 — Cobertura: ¿está todo lo dicho?
Recorrer la transcripción marcando cada dato operativo (volumen, sistema,
persona, proceso, restricción). Cada uno debe estar en la ficha o tener razón
para no estar (small talk, dato personal no operativo). **El error típico no es
inventar: es omitir** el dato dicho de pasada — el tercero que controla las
llaves, el indicador impuesto por fuera, el sistema abandonado.
*Métrica de muestreo: de 10 datos operativos elegidos al azar en la
transcripción, ≥9 deben estar en la ficha.*

## J2 — Fidelidad de interpretación: ¿dice lo que dijeron?
Para cada campo con evidencia, verificar que el valor estructurado sea lo que
la cita respalda — ni más ni menos. "Mil por semana, por ahí" → `~1000/semana`,
no `1000` seco ni `4000/mes`. Los casos límite: cifras corregidas en la misma
sesión (vale la última), unidades ambiguas (¿al día o al mes?), y deseos
expresados como hechos ("queremos un solo número" es deseo en
`decision_del_numero`, no estado actual).

**Nombres propios: la fidelidad también es ortográfica. Y este criterio ya no es
solo autorrevisión: es lo que ejecuta la compuerta.** La transcripción automática
es fonética, y una marca o un apellido mal transcrito viaja hasta el lienzo que el
cliente lee («Gosen casa de Comidas» → «Gocé en casa de comidas»; la telefonista
salió «Sharina», «Yanina» y «Danina» en ocho segundos; «Pixo Gestión» salió
«It's pizza», «BXO», «Pitso» y «Bitso»).

Qué se verifica, en los cuatro lugares donde el contrato lo declara desde v0.3
(`_meta.marca`, `_meta.razon_social`, cada persona, cada sistema): ¿la grafía de
la ficha es una que **alguien de la empresa escribió**, o solo se oyó? Si solo se
oyó, el estado dice `por_confirmar` y `variantes_en_transcripcion` trae las
grafías literales sin corregir. Si dice `confirmada`, `fuente_escrita` nombra
dónde se vio escrita — y el título de la reunión de Teams no cuenta: lo escribió
Ropofy.

Dos fallas simétricas, como en J4: dar por buena la grafía de la transcripción, y
"corregirla" adivinando —que es inferir—. Lo correcto es registrar lo oído,
marcarlo por confirmar y **preguntarlo**, que es exactamente lo que hace la
**compuerta de confirmación de nombres** al cierre de la etapa 1 (`SKILL.md`
§Compuerta). O sea: J2 dejó de ser un criterio que solo se autorrevisa y pasó a
ser el criterio que la compuerta ejecuta con el consultor delante. Ningún script
puede juzgarlo — `validar_ficha.py` bloque I solo verifica que la duda esté bien
declarada.

## J3 — Clasificación de líneas: ¿el eje correcto?
Cada línea con su `sujeto_del_embudo`, `control_del_activo` y
`mecanismo_de_cierre` correctos. Los errores caros: colapsar líneas porque
comparten canal, clasificar al propietario que consigna como demandante, y no
distinguir venta directa de subasta/tercero institucional. Este criterio es el
que más pega aguas abajo: la etapa 3 instancia componentes por estos ejes.

## J4 — Los no_capturado correctos: ¿huecos reales o pereza?
Dos fallas simétricas: marcar no_capturado algo que SÍ se dijo (pereza de
búsqueda — releer antes de marcar), y responder un campo con conocimiento
general del sector (invención — el validador atrapa el caso extremo, no el
sutil). Prueba del sutil: para cada campo respondido, ¿puedo señalar el minuto
de la transcripción que lo respalda?

## J5 — Actores completos: ¿quién falta en la foto?
`personas_declaradas` con función canónica correcta, y —más importante—
`funciones_sin_representacion` con los dueños de proceso que NO estuvieron.
Regla de detección: si alguien en la sesión dice "eso lo maneja X" y X no
habló, X va en ausentes. Es el campo que evita diseñar el flujo de visitas sin
las territoriales (caso Activos) o el call center sin la persona del call
center (caso AYC).

## J6 — Utilidad para la segunda llamada
Leer solo la lista de no_capturado: ¿funciona como agenda de la próxima
conversación? Debe ser accionable ("¿cobran anticipo en línea?", "¿la base
histórica tiene consentimiento de contacto?") y priorizable — los que cambian
el plan o el precio primero. Si la lista es trivial o infinita, la extracción
falló aunque todo lo demás pase.

---

## Cómo se combinan

| Momento | Qué corre |
|---|---|
| Cada ejecución de la skill | `validar_ficha.py` — bloquea la entrega si falla |
| Auto-revisión antes de entregar | J1–J6 como checklist mental, con la transcripción abierta |
| **Cierre de la etapa 1, con el consultor delante** | **J2 sobre los nombres propios, ejecutado por la compuerta de confirmación** (`SKILL.md` §Compuerta). Es el único criterio que no se queda en autorrevisión: se pregunta y se resuelve antes de la etapa 2. En corrida desatendida no bloquea y todo queda `por_confirmar`. |
| Auditoría periódica (1 de cada N fichas) | Humano o Claude evaluador con J1–J6, muestreando 10 datos |
| Compuerta de la etapa 2 | La etapa 2 corre el validador de nuevo antes de consumir la ficha |
