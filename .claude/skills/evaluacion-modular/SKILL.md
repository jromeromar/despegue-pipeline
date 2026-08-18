---
name: evaluacion-modular
description: Etapa 2 de la cadena diagnóstico → propuesta de Ropofy. Evalúa una ficha.json (producida por la skill extraccion-diagnostico) contra el catálogo de fugas y la escala de madurez, y produce diagnostico.json con fugas evidenciadas, madurez 1–4 por módulo, nota /100 y modo A/B. Usar siempre que el usuario pida "evaluar la ficha", "correr la etapa 2", "diagnosticar", "identificar las fugas", "calcular la madurez o la nota" de un cliente, o cuando entregue una ficha.json y pida el siguiente paso. También aplica para reprocesar diagnósticos históricos y construir benchmarks.
---

# Etapa 2 — Evaluación modular

Convierte la `ficha.json` (registro de hechos) en un `diagnostico.json`
(juicios con evidencia). Es la etapa que **sí infiere — pero con correa corta**:
solo fugas que existen en el catálogo, solo madurez que cita hechos de la
ficha, jamás categorías inventadas.

## Compuerta de entrada (obligatoria)

Antes de evaluar, validar la ficha con el validador de la etapa 1:

```
python3 <ruta-skill-extraccion>/scripts/validar_ficha.py ficha-<cliente>.json
```

Si falla, devolver la ficha a la etapa 1 con los errores. No evaluar fichas
inválidas: los juicios sobre datos rotos son peores que no tener juicios.

## Proceso

1. **Leer el catálogo completo** (`references/catalogo-fugas.md`): las seis
   categorías (F fugas, C cegueras, R restricciones de plataforma, O
   restricciones operativas, FP fricción propia, FO fugas del lado oferente),
   el schema de cada fuga y la regla anti-doble-conteo.
2. **Barrido de fugas**: recorrer la ficha buscando síntomas de cada fuga del
   catálogo. Para cada hallazgo, registrar: id del catálogo, evidencia (el
   campo exacto de la ficha + la cita textual que ya trae), cuantificación en
   el modo disponible, y estado (`activa` · `mitigable` · `fuera_de_alcance`).
3. **Elegir la dominante**: una sola, por magnitud del daño según los datos
   del cliente — no por facilidad de venta. Criterio: la que el propio
   entrevistado cuantificó o describió con más carga emocional suele ser la
   correcta, pero la cifra manda sobre la emoción.
4. **Madurez por módulo** (los 7): asignar 0–4 usando la escala de abajo. Cada
   nivel DEBE citar el hecho de la ficha que lo justifica en el campo
   `por_que`. Sin hecho, el nivel es 0 con `por_que: "sin evidencia de
   capacidad instalada"`.
5. **Nota /100**: NUNCA calcularla mentalmente. Correr
   `python3 scripts/calcular_nota.py diagnostico-<cliente>.json` — suma los
   niveles, deriva la letra (F<25, E<40, D<55, C<70, B<85, A≥85) y la escribe
   en el archivo. No maquillar: el promedio del sector es F y eso es
   argumento, no vergüenza.
6. **Salida**: `diagnostico-<cliente>.json` según el schema de
   `references/schema-diagnostico.md`, validado con
   `scripts/validar_diagnostico.py` antes de entregar.

## La escala de madurez (0–4, por módulo)

| Nivel | Nombre | Prueba |
|---|---|---|
| 0 | Inexistente | Nadie mencionó capacidad alguna en ese módulo |
| 1 | Manual | La función existe pero vive en memoria/Excel/conteo a mano |
| 2 | Cubierto | Hay herramienta o proceso estable, sin automatización |
| 3 | Sistematizado | Corre solo cuando el cliente final actúa |
| 4 | Se anticipa | Corre solo cuando NADIE actúa (señales, retomas, umbrales) |

La prueba de cada nivel es la misma de la matriz de fronteras
(`references/matriz-fronteras.md`) — así el diagnóstico y los planes hablan el
mismo idioma y el salto de madurez del lienzo es coherente.

## Trampas conocidas

**Ver la fuga que se quiere vender.** La trampa inversa a la de extracción. La
fuga debe estar en los hechos de la ficha, no en la oferta de Ropofy. Prueba:
si se borra el nombre del componente que la cierra, ¿la fuga sigue estando
descrita en la ficha? Si no, es deseo comercial, no diagnóstico.

**Doble conteo.** El catálogo trae la regla (§4): una misma pérdida no se
cuenta en dos fugas. 3.900 represados alimentan F-08 (volumen desborda) — no
se suman otra vez en F-01 (nadie retoma). Elegir dónde vive la cifra y
referenciarla desde las demás.

**Confundir ceguera con fuga.** C-xx es no poder VER (sin atribución, sin
métrica); F-xx es PERDER (leads, citas, ventas). "No sabemos qué canal
convierte" es C-02 aunque duela como fuga. La distinción importa porque las
cegueras se cierran con tableros y campos, no con automatización.

**El silencio leído como omisión.** Si la ficha no menciona dolores de
Referidos o Reactivación, el módulo va en madurez baja PERO sin fuga inventada.
El silencio es dato de madurez, no licencia para suponer sangría. Registrarlo
en `silencios` con su lectura.

**Fugas de terceros prometidas como cerrables.** Si el control del activo o
del calendario es de un tercero (ficha: `dependencias_externas`), la fuga es
`mitigable`, nunca `activa cerrable`. Se declara qué se puede medir y agilizar,
jamás que se cierra.

**Modo B expresado en pesos.** Sin datos económicos no hay cifras en dinero:
la cuantificación es en volumen y proceso. Poner pesos estimados "del sector"
viola la etapa — eso es exactamente lo que el modo B existe para evitar.

## Checklist antes de entregar

- [ ] Compuerta de entrada corrida (ficha válida)
- [ ] Cada fuga tiene id existente en el catálogo + evidencia trazable a un campo de la ficha
- [ ] Exactamente UNA dominante
- [ ] Cero doble conteo (una cifra vive en una sola fuga)
- [ ] Madurez de los 7 módulos, cada una con `por_que` citando la ficha
- [ ] Silencios registrados como madurez, sin fugas inventadas
- [ ] Cuantificación coherente con el modo (B = volumen/proceso, nunca pesos)
- [ ] La nota la escribió `calcular_nota.py`, no el modelo
- [ ] `validar_diagnostico.py` pasa (exit 0)

## Referencias

- `references/catalogo-fugas.md` — el catálogo completo. Leerlo SIEMPRE antes de evaluar.
- `references/schema-diagnostico.md` — el contrato de salida.
- `references/matriz-fronteras.md` — la escala compartida con los planes.
- `examples/diagnostico-ejemplo-activos.json` — evaluación real: multilínea, modo B, tercero institucional, dominante por volumen.
