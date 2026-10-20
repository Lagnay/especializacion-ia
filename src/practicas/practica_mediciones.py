import time

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
)


if __name__ == "__main__":
    pregunta = (
        "Explica la diferencia entre emoción y sentimiento "
        "en un máximo de 40 palabras."
    )

    latencias = []

    for intento in range(1, 5):
        try:
            url, headers, body = armar_peticion(pregunta)

            inicio = time.perf_counter()
            datos = enviar_peticion(url, headers, body)
            fin = time.perf_counter()

            latencia = fin - inicio
            texto = extraer_texto(datos)
            tokens_salida = datos["usageMetadata"]["candidatesTokenCount"]

            latencias.append(latencia)

            print(f"\nIntento {intento}")
            print("Respuesta:", texto)
            print(f"Tiempo: {latencia:.3f} segundos")
            print("Tokens de salida:", tokens_salida)

        except (TypeError, ValueError, RuntimeError, KeyError) as error:
            print(f"\nIntento {intento} fallido:", error)

    if latencias:
        promedio = sum(latencias) / len(latencias)

        print(f"\nMediciones exitosas: {len(latencias)} de 4")
        print(f"Latencia promedio: {promedio:.3f} segundos")
    else:
        print("\nNo hubo mediciones exitosas para calcular el promedio.")