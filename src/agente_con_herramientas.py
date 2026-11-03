import argparse
import logging
import os

from dotenv import load_dotenv
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

from src.herramientas_tienda import (
    consultar_estado_pedido,
    consultar_stock,
)


logger = logging.getLogger(__name__)


def extraer_texto_agente(salida):
    """Extrae el texto visible de una salida textual o por bloques."""
    return StrOutputParser().invoke(
        AIMessage(content=salida)
    )


def construir_agente(modelo):
    herramientas = [
        consultar_stock,
        consultar_estado_pedido,
    ]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente de una tienda ficticia. "
            "Para consultar existencias utiliza consultar_stock; "
            "para consultar pedidos utiliza consultar_estado_pedido. "
            "Obtén esos datos siempre mediante las herramientas. "
            "Si falta un dato necesario, pide aclaración. "
            "No inventes existencias, estados ni gestiones realizadas. "
            "Ante un saludo responde directamente, sin herramientas. "
            "Responde en español y de forma breve.",
        ),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(
        modelo,
        herramientas,
        prompt,
    )

    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=4,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Ejecuta casos del agente de tienda ficticia."
    )
    parser.add_argument(
        "caso",
        nargs="?",
        default="todos",
        choices=["todos", "stock", "pedido", "combinado", "saludo"],
    )
    argumentos = parser.parse_args()

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

    ejecutor = construir_agente(modelo)

    casos = {
        "stock": (
            "¿Cuántas unidades de arroz quedan en el catálogo ficticio?",
            ["consultar_stock"],
        ),
        "pedido": (
            "¿Cuál es el estado del pedido P-301 del registro ficticio?",
            ["consultar_estado_pedido"],
        ),
        "combinado": (
            "¿Cuántas unidades de leche quedan y cuál es el estado "
            "del pedido P-302? Consulta los datos ficticios disponibles.",
            ["consultar_stock", "consultar_estado_pedido"],
        ),
        "saludo": (
            "Hola, buenos días.",
            [],
        ),
    }

    nombres = (
        list(casos)
        if argumentos.caso == "todos"
        else [argumentos.caso]
    )

    for nombre in nombres:
        entrada, esperadas = casos[nombre]

        print(f"\n=== CASO: {nombre.upper()} ===")
        print("Entrada:", entrada)

        try:
            resultado = ejecutor.invoke({
                "entrada": entrada,
            })

        except Exception:
            logger.exception(
                "No se pudo completar el caso %s.",
                nombre,
            )
            continue

        pasos = resultado["intermediate_steps"]
        usadas = [accion.tool for accion, _ in pasos]

        print("\n=== TRAZA ===")

        for accion, observacion in pasos:
            print("Herramienta:", accion.tool)
            print("Argumentos:", accion.tool_input)
            print("Observación:", observacion)

        print("Herramientas esperadas:", esperadas)
        print("Herramientas utilizadas:", usadas)
        print(
            "Coincide la selección:",
            set(usadas) == set(esperadas),
        )
        print(
            "Respuesta final:",
            extraer_texto_agente(resultado["output"]),
        )