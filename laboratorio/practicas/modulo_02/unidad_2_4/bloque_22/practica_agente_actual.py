import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from src.herramientas_tienda import consultar_stock

from .practica_herramienta_estructurada import (
    consultar_pedido_detallado,
)


def construir_agente_actual(modelo):
    return create_agent(
        model=modelo,
        tools=[
            consultar_stock,
            consultar_pedido_detallado,
        ],
        system_prompt=(
            "Eres un asistente de una tienda ficticia. "
            "Consulta existencias con consultar_stock y pedidos con "
            "consultar_pedido_con_historial. "
            "Si solicitan el historial del pedido, utiliza "
            "incluir_historial=True. "
            "Puedes recuperar del historial de conversación "
            "el pedido mencionado. "
            "Si no conoces el identificador necesario, "
            "pídelo sin inventarlo. "
            "Consulta las herramientas para informar estados "
            "o existencias. "
            "Responde en español y de forma breve."
        ),
        checkpointer=InMemorySaver(),
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

    agente = construir_agente_actual(modelo)

    config = {
        "configurable": {
            "thread_id": "cliente_1",
        }
    }

    estado = agente.get_state(config)

    print("Agente con herramientas y memoria construido.")
    print(
        "Mensajes iniciales:",
        len(estado.values.get("messages", [])),
    )