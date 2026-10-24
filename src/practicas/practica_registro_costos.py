from src.consumir_gemini import calcular_costo


# Referencias del laboratorio fechadas el 16-10-2026.
# Importes en USD por token; no representan un cargo real.
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000
PRECIO_CACHE = 0.03 / 1_000_000

costo_total_sesion = 0.0


def registrar_costo(respuesta: dict) -> float:
    global costo_total_sesion

    costo_estimado = calcular_costo(
        respuesta,
        PRECIO_ENTRADA,
        PRECIO_SALIDA,
        PRECIO_CACHE,
    )

    costo_total_sesion += costo_estimado

    print(
        f"Costo de referencia de la operación: "
        f"{costo_estimado:.9f} USD"
    )
    print(
        f"Acumulado de la sesión: "
        f"{costo_total_sesion:.9f} USD"
    )

    return costo_estimado


if __name__ == "__main__":
    datos_simulados = {
        "usageMetadata": {
            "promptTokenCount": 850,
            "candidatesTokenCount": 320,
            "cachedContentTokenCount": 500,
            "thoughtsTokenCount": 80,
            "totalTokenCount": 1250,
        }
    }

    print("Primera operación simulada")
    registrar_costo(datos_simulados)

    print("\nSegunda operación simulada")
    registrar_costo(datos_simulados)

    print("\nEl programa llegó al final.")