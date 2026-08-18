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
| Auditoría periódica (1 de cada N fichas) | Humano o Claude evaluador con J1–J6, muestreando 10 datos |
| Compuerta de la etapa 2 | La etapa 2 corre el validador de nuevo antes de consumir la ficha |
