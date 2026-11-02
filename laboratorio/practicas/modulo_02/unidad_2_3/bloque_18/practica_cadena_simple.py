import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Falta configurar GEMINI_API_KEY.")

    plantilla = PromptTemplate.from_template(
        "Explica el concepto de {tema} en una oración breve, "
        "para alguien que recién empieza en {area}."
    )

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=api_key,
        vertexai=False,
        timeout=30,
        max_retries=0,
    )

    cadena = plantilla | modelo

    datos = {
        "tema": "tokenización",
        "area": "procesamiento de texto",
    }

    respuesta = cadena.invoke(datos)

    print("Tipo del resultado:", type(respuesta).__name__)
    print("Respuesta:", respuesta.text)