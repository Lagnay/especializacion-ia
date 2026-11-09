# Bloque 24 — Indexación del corpus y persistencia en Chroma

El corpus contiene cinco resúmenes didácticos del código del proyecto.
Cada documento conserva su tema y la ruta del archivo que respalda
su contenido. El divisor recursivo usa un tamaño de 240 caracteres
y un solapamiento de 35.

| Comprobación | Resultado observado |
| --- | --- |
| Documentos y fragmentos | 5 documentos, 6 fragmentos |
| Modelo de embeddings | `gemini-embedding-001` |
| Colección | `proyecto-09ca32e294f70044` |
| Indexación | 6 vectores de 3072 dimensiones |
| Apertura desde otro proceso | 6 vectores recuperados desde disco |
| Pruebas del proyecto | 79 aprobadas |

El primer intento se interrumpió por un fallo de conexión durante
la solicitud de embeddings. Al repetir la indexación, el programa
detectó seis fragmentos pendientes y guardó el lote completo.

La colección se identifica mediante una huella del contenido,
los metadatos, el modelo y la dimensión. El indexador calcula
los embeddings de los fragmentos que faltan en esa colección.
La carpeta `vectorstore/` contiene el índice generado y se excluye
de Git porque puede reconstruirse.

La comprobación de este bloque cubre la indexación y la persistencia.
La calidad de la recuperación se evaluará con preguntas y fragmentos
esperados.