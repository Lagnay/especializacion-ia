import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise SystemExit("Falta GEMINI_API_KEY en el entorno o en .env.")

    modelo = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        api_key=api_key,
        vertexai=False,
    )

    pregunta = "¿Qué hace el cliente si falla la red?"

    try:
        vector = modelo.embed_query(pregunta)
    except Exception as error:
        raise SystemExit(
            f"No se pudo generar el embedding: {error}"
        ) from error

    print("Pregunta:", pregunta)
    print("Dimensiones:", len(vector))
    print("Primeros cinco valores:", vector[:5])