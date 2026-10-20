import time

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
)


if __name__ == "__main__":
    try:
        pregunta = (
            "Explica la diferencia entre emoción y sentimiento "
            "en un máximo de 40 palabras."
        )

        url, headers, body = armar_peticion(pregunta)

        inicio = time.perf_counter()
        datos = enviar_peticion(url, headers, body)
        fin = time.perf_counter()

        latencia = fin - inicio
        texto = extraer_texto(datos)
        uso = datos["usageMetadata"]

        print("Respuesta:", texto)
        print(f"Tiempo observado: {latencia:.3f} segundos")
        print("Tokens de entrada:", uso["promptTokenCount"])
        print("Tokens de salida:", uso["candidatesTokenCount"])

    except (TypeError, ValueError, RuntimeError, KeyError) as error:
        print("No se pudo completar la medición:", error)