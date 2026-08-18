# Schema de propuesta.json — contrato de salida de la etapa 3

El único puente entre el pipeline y el renderizador. El renderizador no conoce
la ficha ni el diagnóstico: todo lo que el lienzo muestra sale de aquí.

```
{
  "_contrato": str,                  // "propuesta v<X>" — versión de este schema
  "cliente": str,
  "titular": str,                    // el hero: la cifra o el dolor, en una frase
  "resumen": str,                    // prosa de "lo que entendimos de su negocio"
  "sesiones": [ str ],
  "modo": "A" | "B",

  "as_is": {                         // sección 1b del lienzo
    "de_donde_llegan": [[canal, nota]],
    "por_donde_pasan": [[quien, nota]],
    "donde_queda":    [[sistema, nota]]
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
