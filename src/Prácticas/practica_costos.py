def calcular_costo(datos, precio_entrada, precio_salida, precio_cache):

    try:
        uso = datos["usageMetadata"]

        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]

    except KeyError as error:
        raise RuntimeError(
            f"Falta un campo necesario para calcular el costo: {error}."
        ) from error

    tokens_cache = uso.get("cachedContentTokenCount", 0)
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

    if not 0 <= tokens_cache <= tokens_entrada:
        raise ValueError(
            "Los tokens en caché deben estar entre cero "
            "y el total de tokens de entrada."
        )
    tokens_entrada_sin_cache = tokens_entrada - tokens_cache
    tokens_salida_facturables = tokens_salida + tokens_razonamiento

    costo_entrada = tokens_entrada_sin_cache * precio_entrada
    costo_cache = tokens_cache * precio_cache
    costo_salida = tokens_salida_facturables * precio_salida

    return costo_entrada + costo_cache + costo_salida


if __name__ == "__main__":
    datos_ejemplo = {
        "usageMetadata": {
            "promptTokenCount": 850,
            "candidatesTokenCount": 320,
            "cachedContentTokenCount": 500,
            "thoughtsTokenCount": 80,
            "totalTokenCount": 1250,
        }
    }

    # Tarifas Standard de pago para Gemini 3.5 Flash-Lite consultadas el 16-10-2026.
    # Datos de consumo preparados para esta prueba.
    precio_entrada = 0.30 / 1_000_000
    precio_salida = 2.50 / 1_000_000
    precio_cache = 0.03 / 1_000_000

    costo = calcular_costo(
        datos_ejemplo,
        precio_entrada,
        precio_salida,
        precio_cache,
    )

    print(f"Costo de referencia: {costo:.9f} USD")