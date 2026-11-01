from langchain_core.prompts import PromptTemplate


if __name__ == "__main__":
    plantilla = PromptTemplate.from_template(
        "Explica el concepto de {tema} en un párrafo, "
        "para alguien que recién empieza en {area}."
    )

    datos = {
        "tema": "tokenización",
        "area": "procesamiento de texto",
    }

    prompt = plantilla.invoke(datos)

    print(prompt.to_string())
    print("Tipo del resultado:", type(prompt).__name__)

    print("\nPrueba con una variable faltante:")

    try:
        prompt_incompleto = plantilla.invoke({
            "tema": "tokenización",
        })
        print(prompt_incompleto.to_string())

    except KeyError:
        print("No se pudo preparar el prompt: falta una variable.")