# Schema de propuesta.json — contrato de salida de la etapa 3

El único puente entre el pipeline y el renderizador. El renderizador no conoce
la ficha ni el diagnóstico: todo lo que el lienzo muestra sale de aquí.

```
{
  "_contrato": str,                  // "propuesta v<X>" — versión de este schema
  "cliente": str,                    // la grafía que se imprime (heredada de ficha._meta.marca.grafia)
  "cliente_grafia_estado": "confirmada" | "por_confirmar",   // v0.3 — heredado de la ficha
  "razon_social": str|null,          // v0.3 — heredado de ficha._meta.razon_social; null si no_capturado
  "nombres_por_confirmar": [         // v0.3 — los nombres propios que ESTA propuesta imprime
    [ que_es, grafia ]               //   y siguen sin confirmar. [] si están todos confirmados.
  ],
  "titular": str,                    // el hero: la cifra o el dolor, en una frase
  "resumen": str,                    // prosa de "lo que entendimos de su negocio"
  "sesiones": [ str ],
  "modo": "A" | "B",

  "as_is": {                         // sección 1b del lienzo
    // Fila = [etiqueta, nota] o [etiqueta, nota, dato_destacado].
    // Los índices 0 y 1 NO cambian de significado (compatibilidad).
    // El tercer elemento es opcional: solo las filas que tienen un dato duro.
    //   dato_destacado = { "cifra": str, "unidad": str }
    "de_donde_llegan": [[canal,   nota, dato_destacado?]],
    "por_donde_pasan": [[quien,   nota, dato_destacado?]],
    "donde_queda":     [[sistema, nota, dato_destacado?]]
  },

  "fugas":   [ …heredadas del diagnóstico tal cual… ],
  "madurez": [ …heredada, con "p": {plan: nivel_al_que_llega} agregado aquí… ],
  "benchmark": { "sector": int, "fuente": str },   // int es puntos /100

  "componentes": {                   // SOLO los que aplican
    "<id>": {
      "id": str,                     // existe en componentes.json
      "nombre_cliente": str,
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

  "no_aplican": [ [nombre_cliente, razon_en_lenguaje_cliente] ],

  "integraciones": [                 // el carril
    [ nombre, nota, "incluido"|"consumo_variable"|"licencia_del_cliente"|"desarrollo_a_cotizar" ]
  ],

  "multiplicador_calculado": {       // INTERNO — nunca texto del cliente
    "1"|"2"|"3": { "piezas": int, "config": int }
  },

  "condicion_comercial": {
    "moneda": str,
    "base_por_plan": { "1": int, "2": int, "3": int },
    "tramos_factor": [[limite, factor]],       // pendientes de validación de negocio
    "precio_por_plan": { "1": int, "2": int, "3": int },   // base × factor, redondeado
    "limite_descuento_sin_aprobacion": float,  // 0.30
    "desglose_interno": str                    // para el panel del consultor
  },

  "plan_recomendado": { "plan": int, "por_que": str },

  "advertencias": [ str ],           // condiciones de arranque; incluye SIEMPRE la regla del copy
  "datos_que_faltan": [ str ]        // heredado si modo B
}
```

## Reglas duras

1. Todo id de `componentes` existe en la librería compilada y su `plan` coincide con el `plan_minimo` de la librería (o superior si el consultor lo subió a mano — dejar rastro en advertencias).
2. Cero componentes con `plan_minimo: null` dentro de `componentes` (V11): van al carril.
3. `precio_por_plan` = base × factor(complejidad) del tramo, verificable aritméticamente.
4. `fugas` y `madurez.hoy` idénticos al diagnóstico de entrada.
5. `no_aplican` no vacío en la práctica: una selección sin exclusiones es sospechosa.
6. Prohibido en todo el archivo: etiquetas HTML, hex de colores, coordenadas, clases CSS.
7. **La cifra del as-is tiene campo propio; no se escarba de la prosa.** Cada
   fila de `as_is` es `[etiqueta, nota]` y, cuando la fila tiene un dato duro,
   `[etiqueta, nota, {"cifra": str, "unidad": str}]`. Reglas, todas duras:
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
   - Una fila sin dato duro **omite** el tercer elemento; no se rellena con una
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

## Nota para el renderizador

`cliente` sigue siendo un **string** y se imprime tal cual; el estado de su
grafía viaja aparte en `cliente_grafia_estado`. Con `por_confirmar`, o con
`nombres_por_confirmar` no vacío, el panel del consultor debería avisarlo antes
de que el documento se envíe al cliente — el dato ya está en el JSON.

El dato destacado de cada fila del as-is se lee de `fila[2]` — **jamás
extrayendo dígitos de `fila[1]`**. Una fila de longitud 2 no tiene cifra: la
fila se dibuja sin número. El contrato garantiza que `fila[2].cifra` aparece
literal en `fila[1]`, así que el número y su frase de respaldo siempre
coinciden.
