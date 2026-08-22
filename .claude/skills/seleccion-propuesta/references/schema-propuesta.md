# Schema de propuesta.json — contrato de salida de la etapa 3

`_contrato: "propuesta v0.5"`

El único puente entre el pipeline y el renderizador. El renderizador no conoce
la ficha ni el diagnóstico: todo lo que el lienzo muestra sale de aquí.

**Regla que gobierna el contrato entero: DATOS, jamás HTML.** Ni color, ni
clase CSS, ni coordenada, ni markup. Si el lienzo parece exigir uno, es que
falta un campo de datos, no una etiqueta.

**Audiencias (v0.5).** El archivo tiene dos lectores: el lienzo del cliente y
el panel del consultor. Todo lo que vive dentro de `panel_interno` es SOLO del
consultor y **jamás se renderiza al cliente**. Todo lo demás es material del
lienzo.

```
{
  "_contrato": str,                  // "propuesta v<X>" — versión de este schema
  "libreria_hash": str,              // v0.4 OBLIGATORIO — el `_meta.version` de la librería
                                     //   compilada contra la que se emitió esta propuesta
  "cliente": str,                    // la grafía que se imprime (heredada de ficha._meta.marca.grafia)
  "cliente_grafia_estado": "confirmada" | "por_confirmar",   // v0.3 — heredado de la ficha
  "razon_social": str|null,          // v0.3 — heredado de ficha._meta.razon_social; null si no_capturado
  "nombres_por_confirmar": [         // v0.3 — los nombres propios que ESTA propuesta imprime
    [ que_es, grafia ]               //   y siguen sin confirmar. [] si están todos confirmados.
  ],
  "titular": str,                    // el hero: la cifra o el dolor, en una frase
  "modo": "A" | "B",

  "resumen": {                       // v0.5 (C1) — deja de ser prosa suelta
    "parrafo": str,                  // 2–3 frases máximo
    "bullets": [str]                 // 3 o 4, nunca más
  },

  "as_is": {                         // sección 1b del lienzo
    // de_donde_llegan y donde_queda: fila = [etiqueta, nota] o
    // [etiqueta, nota, dato_destacado]. Los índices 0 y 1 NO cambian de
    // significado (compatibilidad). El tercer elemento es opcional: solo las
    // filas que tienen un dato duro.
    //   dato_destacado = { "cifra": str, "unidad": str }
    "de_donde_llegan": [[canal,   nota, dato_destacado?]],

    // v0.5 (C2) — por_donde_pasan se vuelve jerárquico: el rol y lo que hace
    // no son sinónimos y no van al mismo nivel.
    "por_donde_pasan": [
      { "quien": str,                //   el rol: "Telefonistas"
        "nota": str,                 //   qué hacen, en una línea
        "detalle": [str],            //   subítems de contexto: cómo lo gestionan,
                                     //   quién hace qué. [] si no hay subítems.
        "dato_destacado": {...}? }   //   opcional, mismas reglas duras del §7
    ],

    "donde_queda":     [[sistema, nota, dato_destacado?]]
  },

  "fugas":   [ …heredadas del diagnóstico tal cual… ],
  "madurez": [ …heredada, con "p": {plan: nivel_al_que_llega} agregado aquí… ],

  "benchmark": {                     // v0.5 (C8 + reconciliación) — ver §11
    "por_modulo": { "<modulo>": float },   // los 7, promedio de la base de comparación
    "fuente": str                    // redacción SIN el tamaño de muestra
  },

  "planes": {                        // v0.5 (C3) — la frontera dicha en el idioma de ESTE negocio
    "1"|"2"|"3": {
      "frontera": str,               // FIJA, de matriz-fronteras.md, no se toca
      "frase": str                   // generada: la frontera traducida a los hechos de la ficha
    }
  },

  "componentes": {                   // SOLO los que aplican
    "<id>": {
      "id": str,                     // existe en componentes.json
      "nombre_cliente": str,
      "sintesis": str,               // v0.5 (C4) — ≤ 90 caracteres, una sola idea, sin jerga
      "conecta_con": [str],          // v0.5 (C5) — ids de componentes de ESTA propuesta
      "plan": "fundamental"|"avanzado"|"inteligente",
      "tipo": str,
      "vis": "front"|"back"|"ambos",
      "journey": int,
      "instancias": int,             // ≥1
      "inst_por": str,               // eje que gobierna la instancia
      "cuota": str|null,             // "hasta 3" si la matriz la define
      "aplica_si": str               // la condición que pasó (trazabilidad)
    }
  },

  "integraciones": [                 // el carril — su posición en el journey NO cambia (Jorge, 21-ago)
    [ nombre, nota, "incluido"|"consumo_variable"|"licencia_del_cliente"|"desarrollo_a_cotizar" ]
  ],

  "brecha_fuera_de_alcance": {       // v0.5 (C6) — presente SOLO si el techo del plan
    "global": {                      //   recomendado es < 100; si llega a 100 se omite ENTERO
      "puntos": int,                 //   escritos por calcular_brecha.py, nunca a mano
      "por_que": str
    },
    "por_modulo": [
      { "m": str,                    //   uno de los 7
        "puntos": int,               //   escritos por calcular_brecha.py
        "por_que": str,              //   qué específicamente lo impide
        "responsable": "cliente" | "tercero" | "regulatorio",
        "que_puede_hacer": str }     //   acción concreta fuera del CRM
    ]
  },

  "condicion_comercial": {
    "moneda": str,
    "base_por_plan": { "1": int, "2": int, "3": int },
    "tramos_factor": [[limite, factor]],       // pendientes de validación de negocio
    "precio_por_plan": { "1": int, "2": int, "3": int },   // base × factor, redondeado
    "limite_descuento_sin_aprobacion": float
    // v0.5: desglose_interno ya no vive aquí — se muda a panel_interno
  },

  "plan_recomendado": { "plan": int, "por_que": str },

  "advertencias": [ str ],           // v0.5 (C10): UNA idea por elemento, ≤ 140 caracteres,
                                     //   redactada para leerse en viñeta. Incluye SIEMPRE
                                     //   la regla del copy.

  "panel_interno": {                 // v0.5 (C7) — SOLO consultor, JAMÁS se renderiza al cliente
    "preguntas_para_el_consultor": [ //   reemplaza a datos_que_faltan: la agenda de Jorge
      { "pregunta": str,             //   redactada para hacerla en voz alta antes de la sesión
        "por_que_importa": str,
        "campo_ficha": str }         //   qué campo de la ficha completaría
    ],
    "no_aplican": [ [nombre_cliente, razon] ],   // antes top-level; mismas reglas
    "multiplicador_calculado": {     //   antes top-level; lo escribe calcular_condicion.py
      "1"|"2"|"3": { "piezas": int, "config": int }
    },
    "desglose_interno": str,         //   antes en condicion_comercial
    "sesiones": [ str ]              //   v0.5 (C9): sale del lienzo, no del expediente
  }
}
```

## Reglas duras

1. Todo id de `componentes` existe en la librería compilada y su `plan` coincide con el `plan_minimo` de la librería (o superior si el consultor lo subió a mano — dejar rastro en advertencias).
2. Cero componentes con `plan_minimo: null` dentro de `componentes` (V11): van al carril.
3. `precio_por_plan` = base × factor(complejidad) del tramo, verificable aritméticamente.
4. `fugas` y `madurez.hoy` idénticos al diagnóstico de entrada.
5. `panel_interno.no_aplican` no vacío en la práctica: una selección sin exclusiones es sospechosa.
6. Prohibido en todo el archivo: etiquetas HTML, hex de colores, coordenadas, clases CSS.
7. **La cifra del as-is tiene campo propio; no se escarba de la prosa.** En
   `de_donde_llegan` y `donde_queda` cada fila es `[etiqueta, nota]` y, cuando
   la fila tiene un dato duro, `[etiqueta, nota, {"cifra": str, "unidad": str}]`.
   En `por_donde_pasan` (objetos desde v0.5) el dato duro va en el campo
   opcional `dato_destacado`, con las mismas reglas. Reglas, todas duras:
   - **Una nota no puede contener más de un token numérico.** Dos números en la
     misma frase hacen imposible saber cuál es el dato de la fila (caso real:
     «ítems de 3 o 4 sectores» terminó mostrando un 3 y un 4 en el lienzo). Se
     reescribe la nota para que lleve una sola cifra, o se parte en dos filas.
     Un rango unido por guion (`20–30`, `7-10`) cuenta como **un** token: es una
     sola cifra. Unido por palabras («3 o 4», «20 a 30») cuenta como dos.
   - **Si la fila declara `cifra`, esa cifra tiene que aparecer en la nota**,
     copiada tal cual (mismos separadores; el guion y los espacios se normalizan
     al comparar). El número que el lienzo destaca debe ser trazable a la frase
     que lo respalda: sin frase que lo sostenga, el número no existe.
   - `cifra` es **texto**, no número: admite rangos (`"20–30"`), aproximaciones
     y separadores de miles (`"1.200"`). El renderizador la muestra, no calcula
     con ella.
   - `unidad` es obligatoria cuando hay `cifra` (`"leads/mes"`,
     `"conversaciones/día"`, `"km"`). No necesita aparecer literal en la nota:
     «conversaciones diarias» → `"conversaciones/día"` es la misma unidad, no
     una invención.
   - Una fila sin dato duro **omite** el dato destacado; no se rellena con una
     cifra sacada de otro lado ni con `null` disfrazado. Si la nota trae un
     número y la fila no lo declara, el validador avisa (advertencia): el lienzo
     simplemente no destacará nada, que es preferible a destacar el número
     equivocado.

8. **El estado de los nombres propios viaja hasta aquí.** La grafía de un nombre
   propio se confirma en la etapa 1 (compuerta de nombres) y esta etapa la
   **hereda sin re-juzgar**, como fugas y madurez: `cliente_grafia_estado`,
   `razon_social` y `nombres_por_confirmar` se copian del estado de la ficha. Un
   nombre sin confirmar no bloquea la propuesta —el validador **advierte**, no
   falla— porque a veces se presenta sabiendo que falta confirmar; lo que no puede
   pasar es presentarlo **sin saberlo**. Si la propuesta corrige una grafía por su
   cuenta, está inventando: la corrección se hace en la ficha y se rehace la
   cadena.

   *Por qué `cliente_grafia_estado` es un campo plano y no `cliente.grafia_estado`:
   `cliente` es la cadena que el lienzo imprime. Convertirla en objeto rompería al
   renderizador el día del merge, igual que habría pasado con las filas del as-is.
   El estado viaja al lado, no dentro.*

9. **`libreria_hash` es obligatorio y decide cómo se valida (v0.4).** La skill de
   selección lo escribe al emitir, copiado del `_meta.version` de la librería
   compilada que usó. No es decorativo: es lo que permite validar una propuesta
   vieja sin romper nada.

   | Caso | Qué hace `validar_propuesta.py` |
   |---|---|
   | `libreria_hash` == hash de la librería con la que se valida | **Validación completa.** Todo id del alcance se verifica contra la librería. |
   | `libreria_hash` distinto del hash actual | La marca **histórica**: valida estructura, aritmética y herencia, pero **no** los ids contra la librería nueva. Sale **0 con advertencia**. |
   | Sin `libreria_hash` y `_contrato` anterior a v0.4 | Histórica por definición: se emitió antes de que el campo existiera. Sale 0 con advertencia. |
   | Sin `libreria_hash` y `_contrato` v0.4+ | **Error.** La skill tenía que escribirlo. |

   El problema que esto resuelve: una corrección de la librería que divide o
   renombra un componente deja a las propuestas ya emitidas apuntando a ids que
   ya no existen. Esas propuestas **no se editan** (regla 7 de la casa: el
   expediente del cliente es su historial), así que la validación tiene que
   entender que son históricas en vez de fallar. Si el alcance de una propuesta
   vieja sigue vigente, se emite `-v2` contra la librería nueva; la vieja se
   queda como historia, y valida.

   La misma lógica aplica al contrato: las propuestas con `_contrato` anterior
   a v0.5 se validan con las reglas de su versión. **El contrato no se
   reescribe hacia atrás.**

10. **`resumen` no repite el as-is (C1, dura).** El resumen dice quiénes son y
    qué les duele; el as-is dice por dónde entra, quién lo gestiona y dónde
    queda. Contenido permitido en `resumen`, y solo este: qué hace la empresa,
    industria, zona de operación, años de experiencia, propuesta de valor, el
    contexto que el cliente dio en la sesión y el problema resumido.
    **Ningún canal, sistema, rol ni cifra que ya aparezca en `as_is` puede
    repetirse en `resumen`.** Operativamente, un *token del as-is* es: (a) cada
    `etiqueta`/`quien` completa, (b) cada palabra de esa etiqueta de ≥ 4 letras
    que no sea conectora, y (c) cada `cifra` declarada. Si un token reaparece
    literal en `resumen` (sin distinguir mayúsculas ni tildes),
    `validar_propuesta.py` falla. `parrafo`: 2–3 frases máximo. `bullets`: 3 o
    4, nunca más.

11. **Benchmark sin muestra (C8).** `benchmark.fuente` se redacta como
    «diagnósticos de PYMES en Colombia y Argentina, antes de implementar
    Ropofy». **Prohibido exponer el tamaño de la muestra** (n) o cualquier
    dígito en `fuente`: el validador lo verifica por regex. `por_modulo` trae
    los 7 módulos con el promedio de la base de comparación; los valores los
    produce el proceso de benchmark, nunca se editan a mano.

12. **Las fronteras de plan son invariantes (C3).** `planes.<n>.frontera` se
    copia textual de estas tres líneas (derivadas de matriz-fronteras.md v1.1,
    filas «Frase» y «El sistema actúa…») y el validador exige el match exacto:
    - `"1"`: **Nada se pierde: el sistema actúa cuando alguien del equipo actúa.**
    - `"2"`: **El sistema trabaja: actúa cuando el cliente final actúa.**
    - `"3"`: **El sistema persigue y decide: actúa cuando nadie actúa.**
    `frase` traduce esa frontera a los hechos de la ficha (canales, roles y
    activos reales del cliente) sin prometer componentes que no están en su
    selección. **Prohibido nombrar en `frase` una capacidad que no exista en
    `componentes` de esta propuesta.** (Regla semántica: la revisa el consultor
    en el checklist; el validador verifica forma y match de frontera.)

13. **`sintesis` (C4).** ≤ 90 caracteres, una sola idea, sin jerga. El detalle
    se levanta después, en la sesión de especificaciones con el consultor; la
    tarjeta del lienzo solo necesita que el cliente entienda qué hace.

14. **`conecta_con` (C5).** Es la relación funcional real (lo que entrega uno
    alimenta al otro), no cercanía visual. Todo id existe en `componentes` de
    la misma propuesta, sin autorreferencia y sin ciclos de longitud 2 (si A
    declara a B, B no declara a A). Si un componente no engrana con nada,
    arreglo vacío — no se fuerza.

15. **`brecha_fuera_de_alcance` (C6).** Presente **solo** si el techo alcanzable
    con el plan recomendado es < 100 (techo = puntos que dan los niveles
    `madurez[].p` del plan recomendado); si llega a 100, el campo se omite
    entero. Los `puntos` (global y por módulo) los escribe
    `scripts/calcular_brecha.py` — nunca el modelo ni la mano — y la suma de
    `por_modulo[].puntos` cuadra con `global.puntos`. `por_modulo` lista solo
    los módulos cuyo techo con el plan recomendado es < 4. Los textos
    (`por_que`, `responsable`, `que_puede_hacer`) son del modelo/consultor y no
    dependen del plan; los `puntos` sí: al cambiar de plan en el lienzo, Atlas
    los recalcula desde `madurez[].p` (misma aritmética del script: déficit de
    niveles × 100/28, redondeo por resto mayor). Propósito comercial: en vez de
    un techo inexplicado, el cliente se lleva la hoja de ruta de lo que le toca
    a él.

16. **`panel_interno` jamás se renderiza al cliente (C7).** Y sus contenidos no
    se duplican fuera: `validar_propuesta.py` falla si `no_aplican`,
    `datos_que_faltan`, `multiplicador_calculado` o `sesiones` aparecen en el
    nivel superior, o si `desglose_interno` sigue dentro de
    `condicion_comercial`. `datos_que_faltan` deja de existir como inventario
    de huecos: se transforma en `preguntas_para_el_consultor`, la agenda de
    preguntas que el consultor hace en voz alta antes de la sesión.

17. **Sin fecha de arranque estimado (C9).** El pipeline no puede derivarla
    hoy. Si más adelante se puede, entra como campo nuevo con semántica de
    **fecha límite de finalización del despegue**, no de estimado.

18. **Advertencias atomizadas (C10).** Cada elemento = una sola idea, ≤ 140
    caracteres, redactada para leerse en viñeta. Si una advertencia mezcla dos
    condiciones, se parte. Se mantiene obligatoria la regla global del copy
    (Ropofy da el punto de partida metodológico; el texto final lo aprueba el
    cliente).

## Nota para el renderizador

`cliente` sigue siendo un **string** y se imprime tal cual; el estado de su
grafía viaja aparte en `cliente_grafia_estado`. Con `por_confirmar`, o con
`nombres_por_confirmar` no vacío, el panel del consultor debería avisarlo antes
de que el documento se envíe al cliente — el dato ya está en el JSON.

El dato destacado de cada fila del as-is se lee de `fila[2]` (o de
`dato_destacado` en `por_donde_pasan`) — **jamás extrayendo dígitos de la
nota**. Una fila sin dato no tiene cifra: se dibuja sin número. El contrato
garantiza que la cifra declarada aparece literal en su nota, así que el número
y su frase de respaldo siempre coinciden.

Nada de `panel_interno` se muestra al cliente. La brecha por módulo se
recalcula al cambiar de plan usando `madurez[].p` (regla 15); los textos de la
brecha no cambian con el plan. El párrafo del plan recomendado se muestra **una
única vez**, en Arquitectura Comercial: la sección de diagnóstico del lienzo
muestra la calificación por módulo, no el plan.

## Changelog

- **v0.5 (21-ago-2026)** — cambios de la sesión de revisión del lienzo con
  Jorge (consultor):
  - **Reconciliación previa de deriva schema/ejemplo**: `ventana` y el
    `multiplicador` escalar del ejemplo v0.3 eran campos nunca contratados y se
    eliminan (gana el schema); `benchmark` adopta la forma por módulo del
    ejemplo (gana el ejemplo en la forma) y suma el `fuente` que el schema
    declaraba (gana el schema en la exigencia) — el `sector: int` nunca se
    implementó y desaparece; las `fugas` de la propuesta vuelven a heredarse
    **tal cual** del diagnóstico (gana el schema): la forma paralela
    `cifra/texto/evidencia/cierra_con/modo` del ejemplo v0.3 era deriva. Si
    Atlas necesita el vínculo fuga→componentes que daba `cierra_con`, entra
    como campo nuevo documentado.
  - C1 `resumen` → `{parrafo, bullets}` + regla anti-redundancia contra as_is.
  - C2 `as_is.por_donde_pasan` → jerárquico `{quien, nota, detalle[]}`;
    `de_donde_llegan` y `donde_queda` quedan igual (Jorge los validó).
  - C3 bloque `planes` con `frontera` invariante + `frase` al negocio.
  - C4 `componentes.<id>.sintesis` (≤ 90).
  - C5 `componentes.<id>.conecta_con`.
  - C6 `brecha_fuera_de_alcance` (+ `scripts/calcular_brecha.py` escribe los puntos).
  - C7 `panel_interno` agrupa lo interno: `preguntas_para_el_consultor`
    (ex-`datos_que_faltan`), `no_aplican`, `multiplicador_calculado`,
    `desglose_interno` y `sesiones`. Campo eliminado: `datos_que_faltan`.
    Campos movidos: `no_aplican`, `multiplicador_calculado`,
    `condicion_comercial.desglose_interno`, `sesiones`.
  - C8 `benchmark.fuente` sin tamaño de muestra (regex de dígitos).
  - C9 `sesiones` sale del lienzo (a `panel_interno`); no se emite fecha de
    arranque estimado.
  - C10 advertencias atomizadas (≤ 140, una idea).
  - No se tocan: `calcular_condicion.py`, la matriz de fronteras (solo
    lectura) y la posición de las integraciones en el journey.
- **v0.4** — `libreria_hash` obligatorio; validación histórica por hash.
- **v0.3** — estado de nombres propios heredado de la ficha
  (`cliente_grafia_estado`, `razon_social`, `nombres_por_confirmar`).
- **v0.2** — dato destacado del as-is con campo propio (`{cifra, unidad}`).
