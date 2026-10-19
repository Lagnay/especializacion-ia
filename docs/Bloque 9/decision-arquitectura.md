# Decisión de arquitectura: elección del modelo

Autor: Slaven Matkovic Baricic  
Fecha: 19-10-2026  
Alcance: miniaplicación de práctica del curso.

## 1. Modelo elegido

Mantengo `gemini-3.5-flash-lite` como modelo predeterminado
de la miniaplicación.

La aplicación actual envía una consulta de texto, extrae
la respuesta y muestra el consumo de tokens y una estimación
de costo a tarifas de pago.

Esta decisión corresponde al laboratorio actual. No determina
todavía el modelo del proyecto integrador.

## 2. Diagrama de arquitectura

La aplicación mantiene la arquitectura documentada en el Bloque 8:

- [Ver diagrama](../Bloque%208/diagrama_arquitectura.drawio.png).
- [Abrir editable de Draw.io](../Bloque%208/diagrama_arquitectura.drawio).

La selección del modelo se realiza mediante el parámetro
`modelo` de `armar_peticion`. Si no se proporciona,
se utiliza `gemini-3.5-flash-lite`.

## 3. Comparación de candidatos

### Tarifas utilizadas

Fuente: [precios oficiales de Gemini](https://ai.google.dev/gemini-api/docs/pricing).

Fecha de consulta: 19-10-2026. Modalidad Standard de pago.

**Gemini 3.5 Flash-Lite**

- Entrada: 0.30 USD por millón de tokens; equivalente a
  0.000300 USD por mil.
- Salida, incluido razonamiento: 2.50 USD por millón;
  equivalente a 0.002500 USD por mil.
- Entrada en caché: 0.03 USD por millón;
  equivalente a 0.000030 USD por mil.

**Gemini 3.6 Flash**

- Entrada: 0.75 USD por millón de tokens; equivalente a
  0.000750 USD por mil.
- Salida, incluido razonamiento: 3.75 USD por millón;
  equivalente a 0.003750 USD por mil.
- Entrada en caché: 0.075 USD por millón;
  equivalente a 0.000075 USD por mil.

Las tarifas indicadas para 3.6 Flash están publicadas hasta
el 31-12-2026. Deben revisarse antes de reutilizar esta comparación.

Los costos estimados no representan necesariamente cargos
reales de mi cuenta. Tampoco incluyen posibles cargos por
herramientas o almacenamiento de caché, que no utilicé
en estas pruebas.

### Método

Utilicé el mismo módulo Python, equipo y conexión para
consultar ambos modelos. Las series se ejecutaron una
después de otra.

Medí con `time.perf_counter()` el tiempo empleado por
`enviar_peticion`: comunicación con el proveedor, comprobación
del estado HTTP y conversión de la respuesta JSON.

No utilicé streaming ni configuré un nivel específico
de razonamiento.

Para comparar latencia y costo repetí cuatro veces la misma
pregunta por modelo. Después realicé una ejecución por modelo
para cada prueba adicional de calidad.

La revisión de las respuestas fue manual.

### Pregunta repetida para medir latencia y costo

> Explica la diferencia entre emoción y sentimiento en un máximo de 40 palabras.

**Gemini 3.5 Flash-Lite**

- Ejecuciones exitosas: 4 de 4.
- Tiempos: 1.075, 1.720, 2.058 y 1.819 segundos.
- Latencia promedio: 1.668 segundos.
- Tokens visibles de salida, promedio: 51.25.
- Tokens de razonamiento: no informados.
- Costo promedio estimado: 0.000133225 USD por consulta.

**Gemini 3.6 Flash**

- Ejecuciones exitosas: 4 de 4.
- Tiempos: 5.224, 5.405, 5.163 y 5.111 segundos.
- Latencia promedio: 5.226 segundos.
- Tokens visibles de salida, promedio: 49.75.
- Tokens de razonamiento, promedio: 763.5.
- Costo promedio estimado: 0.003062438 USD por consulta.

En esta serie, Flash-Lite tardó aproximadamente un tercio
del tiempo de Flash. El costo estimado de Flash fue
aproximadamente 23 veces mayor.

El cálculo incluye los tokens de razonamiento informados.
Los tokens de caché se descuentan de la entrada ordinaria
antes de aplicar su tarifa, para evitar contarlos dos veces.

Cuando los campos opcionales de caché o razonamiento no
aparecen, el cálculo utiliza cero y la consola muestra
«No informado».

### Prueba adicional 1: cálculo y formato

**Pregunta enviada a ambos modelos:**

> Compro 3 cuadernos a 1200 pesos cada uno y 2 lápices a 450 pesos cada uno. Pago con 5000 pesos. Responde únicamente con un objeto JSON válido con las claves 'total' y 'vuelto', cuyos valores deben ser números enteros. No añadas Markdown ni explicaciones.

**Criterios:** cálculo correcto, JSON válido y ausencia
de explicaciones adicionales.

Ambos respondieron correctamente:

```json
{"total": 4500, "vuelto": 500}
```

Resultados de una ejecución por modelo:

- Flash-Lite: 1.936 segundos y 0.000066600 USD estimados.
- Flash: 3.281 segundos y 0.001527750 USD estimados.

### Prueba adicional 2: extracción sin inventar datos

**Pregunta enviada a ambos modelos:**

> Extrae los datos de este mensaje: 'Soy Ana. Necesito 4 paquetes de arroz. Todavía no he decidido cuándo retirarlos'. Devuelve únicamente JSON válido con las claves 'nombre', 'producto', 'cantidad' y 'fecha_retiro'. Usa null para los datos que no estén especificados. No añadas Markdown ni explicaciones.

**Criterios:** extracción correcta, JSON válido y uso
de `null` para la fecha ausente.

Ambos devolvieron los mismos datos:

```json
{
  "nombre": "Ana",
  "producto": "arroz",
  "cantidad": 4,
  "fecha_retiro": null
}
```

El formato de espacios y saltos de línea fue diferente,
pero el contenido fue equivalente.

Resultados de una ejecución por modelo:

- Flash-Lite: 1.911 segundos y 0.000114100 USD estimados.
- Flash: 4.295 segundos y 0.001786500 USD estimados.

### Prueba adicional 3: planificación con restricciones y preferencias

La pregunta evolucionó mediante varias versiones con Flash-Lite.
Para comparar ambos modelos consideré únicamente las respuestas
a esta versión final:

> Necesito que me ayudes, tengo que llevar a lavar si o si mi auto que ya le hace falta, me lo pidieron encarecidamente para una salida importante y me comprometí a llevarlo y traerlo de vuelta, y yo cumplo mi palabra. Además quiero pasar a comprar unas cosas allí en el mismo lugar, pan para comer, leche y nada más. Y para llegar en auto es un tema, los caminos están horribles y la bencina está carísima, además que se mueve mucho y puede derramar la leche. Yo prefiero mil veces traerme las cosas a mano que me sale cómodo, es más fácil y aprovecho de pasear, hacer un poco de actividad física que me hace bien, gasto menos y me ahorro el estrés de manejar, además que me gusta caminar y me hace bien. Para acabar con esto, y encima de todo, en auto por cuestiones de tránsito y dirección de las calles, me demoro 20 minutos y a pie me demoro 5 nada más. ¿Qué opinas tú? ¿Qué me conviene más, ir a comprar en auto o a pie?

**Criterios de evaluación:**

- Cumplir la obligación de llevar el auto a lavar y recuperarlo.
- Aprovechar que las compras están en el mismo lugar.
- Considerar la preferencia por caminar y transportar las compras a mano.
- Comparar el plan completo, no solamente el viaje para comprar.
- No inventar distancias, tiempos o estados emocionales.

**Respuesta completa de Gemini 3.5 Flash-Lite:**

```text
¡Hola! Entiendo perfectamente tu situación. Basándome en todo lo que me cuentas, **te conviene 100% ir a pie a comprar**, y aquí te doy mis razones respaldadas por tus propias palabras:

1. **¡Es más rápido a pie!** Te demoras **5 minutos** caminando versus los **20 minutos** que te toma en auto por culpa del tránsito y el sentido de las calles. ¡Ganas 15 minutos de tu tiempo!
2. **Cuidas el auto (y tu compromiso):** Como te pidieron el auto impecable para la salida importante, ir a pie evita el riesgo de ensuciarlo de nuevo con los caminos horribles o, peor aún, **derramar la leche** dentro del vehículo con los movimientos.
3. **Cuidas tu bolsillo:** La bencina está carísima. Ir a pie significa gastar cero en combustible.
4. **Salud física y mental:** Caminar te sirve como actividad física, aprovechas de pasear, te ahorras el estrés de manejar (que con caminos malos y tráfico es horrible) y te hace bien.
5. **Comodidad con las compras:** Como solo vas a comprar pan y leche, es súper liviano y cómodo para traerlo en la mano.

**En resumen:**
* **El auto** úsalo estrictamente para lo que te comprometiste: llevarlo a lavar y hacer la salida importante.
* **A pie** haz el mandado del pan y la leche.

¡Es la jugada perfecta! Te ahorras estrés, plata, tiempo y mantienes el auto impecable. ¿Qué opinas tú?
```

- Tiempo: 2.761 segundos.
- Costo estimado: 0.000941500 USD.

**Respuesta completa de Gemini 3.6 Flash:**

```text
Por lo que me cuentas, **tienes un dilema claro, pero la solución lógica pasa por combinar ambas cosas**, porque tienes una obligación innegable: **cumplir tu palabra de lavar el auto.**

Si analizamos solo el hecho de **comprar la leche y el pan**, ir a pie gana por goleada: es más rápido (5 min vs. 20 min), más barato, saludable, sin estrés y no corres el riesgo de derramar la leche.

Sin embargo, si solo vas a pie, **no cumples tu compromiso de lavar el auto**.

Por lo tanto, la opción que más te conviene es un **"plan híbrido"** que te permite cumplir tu promesa y a la vez disfrutar de los beneficios de caminar. Te propongo la mejor estrategia:

### La estrategia ideal (Combinada)

1. **Lleva el auto a lavar en auto:** Acepta los 20 minutos de viaje como el "costo" necesario para cumplir tu palabra (que para ti es muy importante).
2. **Deja el auto en el lavadero:** Mientras lo están lavando, **haz las compras a pie.**
3. **Disfruta tu caminata:** Camina esos 5 minutos hasta donde venden el pan y la leche. Haces tu actividad física, te despejas, no te estresas y paseas mientras el auto se limpia.
4. **Para la leche:** Al volver al lavadero, asegura bien la leche en el auto (puedes trabarla en el piso del asiento del acompañante o pegada al respaldo para que no se tumbe con los baches) y te vuelves a casa con el auto limpio y las compras hechas.

---

### Opción alternativa (En dos tiempos)

Si de verdad te da pánico que la leche se derrame en el auto por lo mal que está el camino:
1. **Ve primero a pie** a comprar el pan y la leche, los dejas en tu casa tranquilos y disfrutas tu paseo de 5 minutos.
2. **Luego sales en el auto** únicamente a llevarlo al lavadero.

### Conclusión
**No te conviene ir en auto *solo* a comprar, pero sí te conviene ir en auto *para lavarlo*.** La mejor opción es llevar el auto a lavar y hacer la compra a pie mientras esperas. Así cumples tu palabra, ahorras tiempo muerto de espera, caminas y te estresas mucho menos.
```

- Tiempo: 12.159 segundos.
- Costo estimado: 0.006247500 USD.

**Evaluación:**

Flash-Lite dio demasiado peso a las preferencias por caminar.
Separó las tareas sin demostrar que su propuesta resultara
más conveniente al considerar también el lavado obligatorio.

Flash identificó mejor la obligación principal y propuso
combinar las tareas, pero añadió información no proporcionada:
atribuyó cinco minutos al trayecto entre lavadero y compras,
y describió como «pánico» una preocupación expresada
en términos diferentes.

La solución que considero mejor ajustada era llevar el auto,
dejarlo lavando, hacer las compras, transportarlas a casa
caminando y regresar a recoger el auto.

Así se combinan el lavado obligatorio, las compras y una
caminata de aproximadamente diez minutos si el regreso
a pie tarda lo mismo que la ida.

Ninguno de los dos modelos propuso ese plan completo.

### Candidato exploratorio descartado: Gemini 3.8 Flash

Antes de completar la comparación final probé `gemini-3.8-flash`.

Obtuve una respuesta exitosa, pero también varios tiempos
de espera agotados y un error HTTP 503.

Lo descarté como candidato para esta comparación por la
intermitencia observada durante las pruebas. No modifiqué
credenciales para intentar resolver esos fallos.

Estos resultados no demuestran que el modelo sea siempre
inestable ni permiten atribuir todos los fallos a una
causa concreta.

No mezclé esas ejecuciones con los promedios de los
dos candidatos finales.

### Limitaciones

- La muestra es pequeña y corresponde a este laboratorio.
- Las tareas adicionales tuvieron una ejecución por modelo.
- Los tiempos dependen también de la conexión y del proveedor.
- No se compararon configuraciones equivalentes de razonamiento:
  se utilizó el comportamiento predeterminado de cada modelo.
- Los costos y tiempos de tareas diferentes se mantienen separados.
- Una petición que termina en timeout no permite concluir
  que el proveedor no haya consumido recursos.
- No se ha demostrado que los resultados se mantengan
  para otros dominios, volúmenes o preguntas.

## 4. Justificación

Prioricé que la miniaplicación resolviera consultas sencillas
con poca espera y bajo costo estimado.

Ambos modelos resolvieron correctamente las pruebas de
cálculo y extracción. En la serie repetida, Flash-Lite
ofreció menor latencia y menor costo estimado.

La prueba de planificación mostró que esa elección tiene
límites: Flash-Lite no integró adecuadamente todas las
restricciones y preferencias del mensaje.

Por ello, lo mantengo como modelo predeterminado para
el alcance actual del laboratorio, sin considerarlo una
solución validada para decisiones complejas sin revisión.

## 5. Alternativas descartadas y revisión futura

No seleccioné `gemini-3.6-flash` como modelo predeterminado:
su mejora parcial en planificación no eliminó los errores,
y su mayor tiempo y costo estimado no se justificaron
para las tareas sencillas del laboratorio.

Descarté `gemini-3.8-flash` de la comparación final por
los fallos e intermitencia observados durante mis pruebas.

Esta decisión no impide utilizar más adelante estos modelos
u otros de mayor capacidad cuando una evaluación específica
demuestre que aportan una mejora necesaria.

Revisaré la elección si cambian los requisitos, los modelos,
los precios o los resultados observados.