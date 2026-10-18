from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costo,
)


if __name__ == "__main__":
    try:
        pregunta = "Dime únicamente cuál es la capital de Escocia."

        url, headers, body = armar_peticion(pregunta)
        datos = enviar_peticion(url, headers, body)

        texto = extraer_texto(datos)
        uso = datos["usageMetadata"]

        print("Respuesta:", texto)
        print("Tokens de entrada:", uso["promptTokenCount"])
        print("Tokens de salida:", uso["candidatesTokenCount"])
        print("Tokens totales:", uso["totalTokenCount"])
        print("Tokens de entrada en caché:",uso.get(
            "cachedContentTokenCount", "No informado"),)
        print("Tokens de razonamiento:", uso.get(
            "thoughtsTokenCount", "No informado"),)
        # Tarifas Standard de pago para Gemini 3.5 Flash-Lite.
        # Consultadas el 16-10-2026.
        precio_entrada = 0.30 / 1_000_000
        precio_salida = 2.50 / 1_000_000
        precio_cache = 0.03 / 1_000_000

        costo = calcular_costo(
            datos,
            precio_entrada,
            precio_salida,
            precio_cache,
        )

        print(f"Costo de referencia a tarifa de pago: {costo:.9f} USD")

    except (TypeError, ValueError, RuntimeError, KeyError) as error:
        print("No se pudo completar la práctica:", error)