import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Falta configurar GEMINI_API_KEY.")

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        api_key=api_key,
        vertexai=False,
        timeout=30,
        max_retries=0,
    )

    respuesta = modelo.invoke(
        "Explica qué es la tokenización en una sola oración breve."
    )

    print("Tipo del resultado:", type(respuesta).__name__)
    print("Contenido recibido:", respuesta.content)
    print("Texto:", respuesta.text)