from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
)


if __name__ == "__main__":
    instruccion = (
        "Eres un profesor de Python para principiantes. "
        "Responde en español con un máximo de tres oraciones. "
        "Si falta información, indícalo sin inventarla."
    )

    pregunta = "¿Qué es una función?"

    try:
        url, headers, body = armar_peticion(
            pregunta,
            system_instruction=instruccion,
        )

        datos = enviar_peticion(url, headers, body)
        texto = extraer_texto(datos)

        print("Respuesta:", texto)

    except (TypeError, ValueError, RuntimeError) as error:
        print("No se pudo completar la consulta:", error)