# Schema de diagnostico.json — contrato de salida de la etapa 2

`_contrato: "diagnostico v0.2"`

```
{
  "_contrato": str,                 // "diagnostico v<X>" — versión de este schema (v0.2+)
  "_meta": {
    "cliente": str,
    "ficha_fuente": str,            // archivo de ficha evaluado
    "version_catalogo": str,        // versión del catálogo de fugas usada
    "evaluado_por": str,
    "fecha": str
  },

  "modo": "A" | "B",                // heredado de la ficha, nunca recalculado

  "fugas": [
    {
      "id": str,                    // DEBE existir en el catálogo (F/C/R/O/FP/FO-xx)
      "titulo": str,                // la frase protagonista — ver regla 7
      "categoria": "fuga"|"ceguera"|"restriccion"|"friccion_propia"|"fuga_oferente",
      "dominante": bool,            // exactamente una en true
      "estado": "activa"|"mitigable"|"fuera_de_alcance",
      "evidencia_ficha": str,       // ruta del campo, ej. "F_calidad.volumenes.represados"
      "evidencia_textual": str,     // la cita «…» que la ficha ya trae — subordinada al titulo
      "cuantificacion": {
        "valor": str,               // "3.900 conversaciones" | "sin métrica de visitas"
        "unidad": "volumen"|"proceso"|"dinero",   // dinero SOLO en modo A
        "vive_aqui": bool           // regla anti-doble-conteo: la cifra pertenece a esta fuga
      },
      "absorbe": [str]?,            // v0.2 (C11) — SOLO en una fuga consolidada: los ids del
                                    //   catálogo que esta fuga acapara. Trazabilidad, no adorno.
      "depende_de_tercero": str|null   // quién, si estado=mitigable
    }
  ],

  "madurez": [
    {
      "m": "Gestión"|"Atracción"|"Nutrición"|"Cierre"|"Reactivación"|"Referidos y Fidelización"|"Tableros",
      "hoy": 0-4,
      "por_que": str                // v0.2 (C12): 2–3 frases — el hecho citado de la ficha,
                                    //   qué nivel implica y qué falta para el siguiente
    }
  ],                                // los 7, siempre

  "nota": { "puntos": 0-100, "letra": "F"|"E"|"D"|"C"|"B"|"A" },

  "silencios": [
    { "modulo": str, "lectura": str }   // lo no mencionado, leído como madurez
  ],

  "advertencias": [ str ],          // condiciones de arranque que la etapa 3 debe respetar

  "datos_que_faltan_para_modo_A": [ str ]   // presente si modo=B
}
```

## Reglas duras

1. Todo `id` existe en el catálogo. Inventar ids es la falla capital de la etapa.
2. Exactamente una fuga con `dominante: true`.
3. `cuantificacion.unidad = "dinero"` solo si `modo = "A"`.
4. Los 7 módulos presentes en `madurez`, cada uno con `por_que` no vacío.
5. Una cifra vive en UNA fuga (`vive_aqui: true`); las demás la referencian sin
   sumarla. La regla aplica también **entre una fuga consolidada y las que
   absorbió** (v0.2): la cifra de una fuga absorbida no reaparece como dueña en
   otra entrada.
6. Este archivo no menciona componentes, planes ni precios: eso es etapa 3.
7. **`titulo` es la frase protagonista (C11).** Corta (≤ 60 caracteres), en
   lenguaje del cliente, y **sin la palabra «fuga» dentro** — el encabezado de
   sección ya la dice. `evidencia_textual` es subordinada: sostiene al título,
   no compite con él.
8. **Tope de fugas (C11, duro).** Máximo **5** elementos con
   `categoria: "fuga"`. Si el catálogo dispara más, se consolidan en una fuga
   más general que las acapare, registrando los ids absorbidos en `absorbe`
   para no perder trazabilidad. Reglas de `absorbe`:
   - todo id existe en el catálogo;
   - un id absorbido **no** aparece además como entrada propia en `fugas`;
   - solo consolida lo conectado de verdad (el criterio de Jorge: «todo el
     gasto de atracción desemboca en la misma persona y el mismo número, nadie
     sabe de dónde vino» — esas van juntas).
   **Cegueras y restricciones no se consolidan ni se recortan**: van explícitas
   y separadas («la ceguera es otra forma de explicar lo que termina siendo una
   fuga»).
9. **`por_que` de madurez ampliado (C12).** 2–3 frases por módulo: el hecho
   citado de la ficha, qué nivel implica y qué falta para el siguiente. El
   validador exige el mínimo de longitud. La calificación por módulo ocupa el
   espacio del lienzo que dejaba el párrafo del plan recomendado; el plan
   recomendado sigue viviendo solo en `plan_recomendado` de la propuesta, que
   el lienzo muestra una única vez, en Arquitectura Comercial.

## Diagnósticos anteriores a v0.2

Los diagnósticos sin `_contrato` se emitieron antes de esta versión: el
validador les aplica las reglas de su época (advierte sobre las nuevas, no
bloquea). El contrato no se reescribe hacia atrás; al reprocesar, el archivo
nuevo sale v0.2.

## Changelog

- **v0.2 (21-ago-2026)** — sesión de revisión del lienzo con Jorge:
  - C11: tope duro de 5 `categoria: "fuga"` con consolidación trazable
    (`absorbe`); cegueras y restricciones intactas; `titulo` protagonista,
    ≤ 60, sin la palabra «fuga»; anti-doble-conteo extendido a consolidadas.
  - C12: `madurez[].por_que` pasa a 2–3 frases (hecho + nivel + qué falta);
    sube el mínimo del validador.
  - Se agrega `_contrato` al archivo (antes solo `_meta.version_catalogo`).
- **v0.1** — versión inicial (sin `_contrato` declarado).
