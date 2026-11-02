# Bloque 19 — Enrutamiento condicional con LangChain

Autor: Slaven Matkovic Baricic.

## Objetivo y diseño

Implementé un flujo que clasifica mensajes de clientes y selecciona
un tratamiento según su intención principal.

El flujo tiene cuatro rutas:

- Pregunta: responde usando información confirmada del ejercicio.
- Queja: reutiliza la cadena de análisis, planificación y redacción
  del Bloque 18.
- Sugerencia: reconoce la propuesta sin prometer su implementación.
- Desconocida: devuelve un mensaje fijo para pedir aclaración.

El contexto y los mensajes utilizados son ficticios.
La ejecución de generación se realizó con la API real de Gemini.

## Componentes

El módulo reutilizable está en `src/enrutamiento.py`.

Sus funciones son:

- `normalizar_categoria`: prepara el formato de la etiqueta.
- `construir_paso_clasificacion`: construye el clasificador.
- `construir_rutas`: construye los tratamientos disponibles.
- `construir_cadena_con_enrutamiento`: conecta un clasificador
  con las rutas recibidas.
- `construir_flujo_atencion`: construye el flujo completo.

El modelo se recibe como parámetro. Construir el flujo no ejecuta
las consultas.

`RunnablePassthrough.assign` conserva el mensaje y añade
la etiqueta normalizada y la respuesta.

`RunnableBranch` evalúa las condiciones en orden y ejecuta
una sola ruta.

## Categorías y normalización

El clasificador recibe instrucciones para devolver:

- `pregunta`.
- `queja`.
- `sugerencia`.
- `desconocida`.

Una consulta con forma interrogativa puede clasificarse como queja
si comunica un problema que requiere atención.

La normalización elimina espacios exteriores, convierte a minúsculas
y admite un punto final. No interpreta frases ni extrae palabras.

Por ejemplo:

- `" Queja.\n"` se convierte en `"queja"`.
- `"queja urgente"` permanece como `"queja urgente"`.

El campo `categoria` conserva la etiqueta normalizada; eso no
garantiza que pertenezca a las categorías admitidas.

Preguntas, quejas y sugerencias tienen condiciones explícitas.
Cualquier otra etiqueta utiliza la ruta desconocida.

Esta decisión amplía el ejemplo de la guía, donde la ruta de
pregunta también funcionaba como ruta por defecto.

La ruta desconocida atiende etiquetas no reconocidas.
No captura excepciones del proveedor.

## Reproducción

Desde la raíz del repositorio, con el entorno virtual activo,
las dependencias instaladas y `GEMINI_API_KEY` configurada en `.env`:

```powershell
python -m src.enrutamiento
```

El programa ejecuta los cuatro casos definidos en el módulo.
La categoría esperada se utiliza para comparar después de ejecutar;
no se envía al modelo.

Configuración utilizada:

- Modelo: `gemini-3.5-flash-lite`.
- Timeout configurado: 30 segundos por solicitud.
- Reintentos automáticos: desactivados.

Invocaciones previstas al modelo por entrada, cuando el flujo
se completa correctamente:

| Ruta seleccionada | Clasificación | Tratamiento | Total |
| --- | ---: | ---: | ---: |
| Pregunta | 1 | 1 | 2 |
| Queja | 1 | 3 | 4 |
| Sugerencia | 1 | 1 | 2 |
| Desconocida | 1 | 0 | 1 |

Con las categorías esperadas para estos cuatro casos, el diseño
prevé nueve invocaciones al modelo. Este conteo se deduce de la
estructura del flujo; no es una medición independiente de solicitudes
HTTP ni de cargos.

## Salida completa de la ejecución

```text
=== MENSAJE ===
¿Qué información debo indicar cuando solicito la factura de un pedido?
Categoría esperada: pregunta
Etiqueta normalizada: 'pregunta'
Coincide con la esperada: True
Respuesta: Para solicitar la factura, debes escribir al canal de soporte de la tienda e indicar el número del pedido.

=== MENSAJE ===
El pedido P-205 debía llegar el martes y llegó el miércoles. Compré dos cartones de leche y recibí uno. Pagué el pedido completo y necesito la factura por correo. Prefiero recibir el producto faltante antes que un reembolso. Puedo recibir entregas de 18 a 20, previa confirmación. Por favor, contáctenme por escrito.
Categoría esperada: queja
Etiqueta normalizada: 'queja'
Coincide con la esperada: True
Respuesta: Estimado/a cliente,

Hemos recibido su mensaje sobre el pedido P-205 y lamentamos los inconvenientes con la demora en la entrega y el faltante del cartón de leche. Tomamos nota de que pagó el pedido completo, de su solicitud de recibir el producto faltante en lugar de un reembolso, de su necesidad de recibir la factura por correo electrónico y de su disponibilidad de 18:00 a 20:00, previa confirmación.

Antes de poder confirmar una solución o coordinar cualquier acción, necesitamos verificar los registros internos de despacho y de pagos para contrastar lo ocurrido. Nos pondremos en contacto con usted por escrito a la brevedad una vez realizadas estas revisiones.

Agradecemos su comprensión y paciencia.

Atentamente,
Atención al cliente

=== MENSAJE ===
Me gustaría que la tienda permitiera elegir una franja horaria al hacer el pedido.
Categoría esperada: sugerencia
Etiqueta normalizada: 'sugerencia'
Coincide con la esperada: True
Respuesta: ¡Hola!

Muchas gracias por hacernos llegar tu sugerencia. Comprendemos perfectamente tu punto, ya que poder elegir una franja horaria sin duda haría que la recepción de los pedidos sea mucho más cómoda y adaptada a los tiempos de cada cliente.

Agradecemos mucho que te hayas tomado el tiempo de compartirlo con nosotros.

=== MENSAJE ===
Hola, buenos días.
Categoría esperada: desconocida
Etiqueta normalizada: 'desconocida'
Coincide con la esperada: True
Respuesta: ¿Podrías explicar qué necesitas? Puedes hacer una consulta, describir un problema o proponer una mejora.
```

## Revisión de los resultados

Las cuatro etiquetas coincidieron con las categorías esperadas.

| Caso | Revisión de la respuesta |
| --- | --- |
| Pregunta | Indica el canal de soporte y el número de pedido, conforme al contexto ficticio proporcionado. |
| Queja | Reconoce demora y faltante; conserva factura, solución preferida, horario y contacto escrito. Añade una promesa de contacto «a la brevedad» sin respaldo operativo del programa. |
| Sugerencia | Reconoce la mejora propuesta sin afirmar que se haya registrado, evaluado o aprobado. |
| Saludo | Devuelve el mensaje fijo de aclaración previsto. |

La coincidencia de categorías no demuestra por sí sola la calidad
de las respuestas.

El resultado de queja sigue siendo un borrador para revisión:
el programa no consulta registros de pedidos, verifica pagos,
coordina entregas ni realiza contactos posteriores.

## Pruebas automatizadas

Archivo: `tests/test_enrutamiento.py`.

```powershell
python -m pytest tests/test_enrutamiento.py -v
```

Resultado observado: 14 pruebas pasadas.

- Seis casos de selección de rutas.
- Siete casos de clasificación con normalización.
- Una prueba del flujo completo de clasificación y atención de queja.

Las pruebas verifican que construir la cadena no ejecute sus
componentes, que solo se invoque la ruta seleccionada y que
se conserven el mensaje y la categoría.

Utilizan `MagicMock` y, cuando corresponde, respuestas `AIMessage`.
No consultan Gemini ni evalúan la calidad de sus respuestas reales.

Comprobación completa:

```powershell
python -m pytest tests -v
```

Resultado observado: 54 pruebas pasadas y una advertencia.

La advertencia es un `DeprecationWarning` procedente de
`google/genai/types.py`, relacionado con `_UnionGenericAlias`.
No impidió que las pruebas pasaran.

## Límites y ampliación

- La clasificación puede variar o ser incorrecta.
- La normalización admite variaciones concretas de formato;
  no corrige cualquier salida inesperada.
- Una etiqueta no reconocida utiliza la ruta de aclaración.
- Las excepciones del proveedor todavía se propagan.
- El flujo no incorpora los reintentos ni el registro de costos
  de `src/cliente.py`.
- Los borradores requieren revisión humana.
- Cuatro casos no demuestran fiabilidad general.

Para incorporar otra categoría, como `elogio`, habría que actualizar
las instrucciones del clasificador, construir su tratamiento,
añadir su condición antes de la ruta por defecto y agregar
las pruebas y los casos de evaluación correspondientes.