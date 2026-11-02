import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from src.practicas.practica_normalizacion_categoria import (
    normalizar_categoria,
)


def construir_paso_clasificacion(modelo):
    plantilla = PromptTemplate.from_template(
        "Clasifica la intención principal del mensaje de un cliente.\n\n"
        "Categorías:\n"
        "- queja: informa un problema o incumplimiento "
        "y busca atención, aunque lo formule como una pregunta.\n"
        "- pregunta: solicita información sin plantear "
        "un problema concreto ni una propuesta de mejora.\n"
        "- sugerencia: propone una mejora.\n"
        "- desconocida: es un saludo, no contiene información "
        "suficiente o no permite identificar una intención clara.\n\n"
        "Si el mensaje combina un problema concreto que requiere "
        "atención con una propuesta de mejora, prioriza queja. "
        "Devuelve únicamente una de estas palabras: "
        "pregunta, queja, sugerencia o desconocida. "
        "No respondas al cliente ni expliques tu clasificación.\n\n"
        "Mensaje:\n{mensaje}"
    )

    return (
        plantilla
        | modelo
        | StrOutputParser()
        | normalizar_categoria
    )


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

    paso_clasificacion = construir_paso_clasificacion(modelo)

    mensaje = (
        "Mi pedido llegó incompleto: compré dos cartones de leche "
        "y recibí solamente uno. Necesito que revisen lo ocurrido."
    )

    categoria = paso_clasificacion.invoke({
        "mensaje": mensaje,
    })

    print("Mensaje:", mensaje)
    print("Categoría:", repr(categoria))