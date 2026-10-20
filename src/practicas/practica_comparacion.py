import time

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costo,
)


if __name__ == "__main__":
    modelo_elegido = "gemini-3.6-flash"
    cantidad_intentos = 1

    pregunta = (
     "Extrae los datos de este mensaje: "
    "'Soy Ana. Necesito 4 paquetes de arroz. "
    "Todavía no he decidido cuándo retirarlos'. "
    "Devuelve únicamente JSON válido con las claves "
    "'nombre', 'producto', 'cantidad' y 'fecha_retiro'. "
    "Usa null para los datos que no estén especificados. "
    "No añadas Markdown ni explicaciones."
    )

    # Tarifas Standard de pago consultadas el 19-10-2026.
    precio_entrada = 0.75 / 1_000_000
    precio_salida = 3.75 / 1_000_000
    precio_cache = 0.075 / 1_000_000

    latencias = []
    costos = []

    print("Modelo solicitado:", modelo_elegido)

    for intento in range(1, cantidad_intentos + 1):
        try:
            url, headers, body = armar_peticion(
                pregunta,
                modelo=modelo_elegido,
            )

            inicio = time.perf_counter()
            datos = enviar_peticion(url, headers, body)
            fin = time.perf_counter()

            latencia = fin - inicio
            texto = extraer_texto(datos)
            uso = datos["usageMetadata"]

            costo = calcular_costo(
                datos,
                precio_entrada,
                precio_salida,
                precio_cache,
            )

            latencias.append(latencia)
            costos.append(costo)

            print(f"\nIntento {intento}")
            print("Modelo devuelto:", datos.get("modelVersion", "No informado"))
            print("Respuesta:", texto)
            print(f"Tiempo: {latencia:.3f} segundos")
            print("Tokens de entrada:", uso["promptTokenCount"])
            print("Tokens de salida:", uso["candidatesTokenCount"])
            print(
                "Tokens de razonamiento:",
                uso.get("thoughtsTokenCount", "No informado"),
            )
            print(
                "Tokens en caché:",
                uso.get("cachedContentTokenCount", "No informado"),
            )
            print(f"Costo de referencia: {costo:.9f} USD")

        except (TypeError, ValueError, RuntimeError, KeyError) as error:
            print(f"\nIntento {intento} fallido:", error)
            print("Tipo de error original:", type(error.__cause__).__name__)

    if latencias:
        promedio_latencia = sum(latencias) / len(latencias)
        promedio_costo = sum(costos) / len(costos)

        print(f"\nMediciones exitosas: "f"{len(latencias)} de {cantidad_intentos}")
        print(f"Latencia promedio: {promedio_latencia:.3f} segundos")
        print(f"Costo promedio de referencia: {promedio_costo:.9f} USD")
    else:
        print("\nNo hubo mediciones exitosas.")