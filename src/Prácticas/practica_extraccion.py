from src.consumir_gemini import extraer_texto


def probar_extraccion(nombre, datos):
    print(f"\n=== {nombre} ===")

    try:
        resultado = extraer_texto(datos)
    except RuntimeError as error:
        print("Error detectado:", error)
    else:
        print("Texto extraído:", resultado)


probar_extraccion(
    "CAMPO FALTANTE",
    {}
)

probar_extraccion(
    "LISTA VACÍA",
    {"candidates": []}
)

datos_validos = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {"text": "Respuesta de prueba."}
                ]
            }
        }
    ]
}

probar_extraccion(
    "RESPUESTA VÁLIDA",
    datos_validos
)