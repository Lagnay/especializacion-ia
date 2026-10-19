import json
import re


def parsear_respuesta_json(texto):
    texto_limpio = texto.strip()

    texto_limpio = re.sub(
        r"^```(?:json)?\s*",
        "",
        texto_limpio,
    )
    texto_limpio = re.sub(
        r"\s*```$",
        "",
        texto_limpio,
    )

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError as error:
        raise ValueError(
            "La respuesta del modelo no es JSON válido."
        ) from error

    if not isinstance(datos, dict):
        raise ValueError(
            "La respuesta debe contener un objeto JSON."
        )

    return datos


if __name__ == "__main__":
    casos = [
        '{"categoria": "soporte_tecnico", "confianza": 0.99}',
        '```json\n{"categoria": "compras", "confianza": 0.8}\n```',
        '{"categoria": }',
        '["soporte_tecnico"]',
    ]

    for numero, texto in enumerate(casos, start=1):
        print(f"\nCaso {numero}")

        try:
            resultado = parsear_respuesta_json(texto)
            print("Datos interpretados:", resultado)
        except ValueError as error:
            print("Error controlado:", error)

    print("\nEl programa llegó al final.")