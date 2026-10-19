import json

from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
)


if __name__ == "__main__":
    instruccion = (
        "Clasifica el mensaje del usuario. "
        "Responde únicamente con un objeto JSON válido, "
        "sin explicaciones ni bloques de Markdown. "
        "Incluye las claves 'categoria' y 'confianza'. "
        "La categoria debe ser 'soporte_tecnico', 'compras' u 'otro'. "
        "La confianza debe ser un número entre 0 y 1."
    )

    pregunta = (
        "Necesito restablecer mi contraseña, "
        "pero no recibo el correo de verificación."
    )

    try:
        url, headers, body = armar_peticion(
            pregunta,
            system_instruction=instruccion,
        )

        respuesta_api = enviar_peticion(url, headers, body)
        texto_generado = extraer_texto(respuesta_api)

        print("Texto generado:", texto_generado)
        print("Tipo antes de convertir:", type(texto_generado))

        datos_generados = json.loads(texto_generado)

        if not isinstance(datos_generados, dict):
            raise ValueError(
                "La respuesta debe contener un objeto JSON."
            )

        print("Tipo después de convertir:", type(datos_generados))
        print("Categoría:", datos_generados["categoria"])
        print("Confianza:", datos_generados["confianza"])

    except json.JSONDecodeError as error:
        print("El texto generado no es JSON válido:", error)

    except (TypeError, ValueError, RuntimeError, KeyError) as error:
        print("No se pudo procesar la consulta:", error)