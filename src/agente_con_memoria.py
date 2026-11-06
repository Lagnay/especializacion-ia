import argparse
import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from src.herramientas_pedidos import consultar_pedido_detallado
from src.herramientas_tienda import consultar_stock


logger = logging.getLogger(__name__)


def construir_agente_con_memoria(modelo):
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
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta una conversación con memoria "
            "y sesiones separadas."
        )
    )
    parser.add_argument(
        "--ejecutar",
        action="store_true",
        help="Realiza las consultas reales a Gemini.",
    )
    argumentos = parser.parse_args()

    if not argumentos.ejecutar:
        print("Modo de preparación: no se ejecutaron consultas.")
        print("Para realizar las consultas, añade --ejecutar.")
        parser.exit()
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

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

    agente = construir_agente_con_memoria(modelo)

    config_1 = {
        "configurable": {
            "thread_id": "cliente_1",
        },
        "recursion_limit": 12,
    }
    config_2 = {
        "configurable": {
            "thread_id": "cliente_2",
        },
        "recursion_limit": 12,
    }

    consultas = [
        (
            "CLIENTE 1 - TURNO 1",
            config_1,
            "¿Cuál es el estado del pedido P-301? "
            "Incluye su historial de estados.",
        ),
        (
            "CLIENTE 1 - TURNO 2",
            config_1,
            "¿Y ese mismo pedido ya fue entregado?",
        ),
        (
            "CLIENTE 2 - SESION NUEVA",
            config_2,
            "¿Qué pedido te mencioné antes?",
        ),
    ]

    for titulo, config, pregunta in consultas:
        cantidad_previa = len(
            agente.get_state(config).values.get("messages", [])
        )

        print("\n===", titulo, "===")
        print("Entrada:", pregunta)
        print("Mensajes previos:", cantidad_previa)

        try:
            resultado = agente.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": pregunta,
                        }
                    ]
                },
                config=config,
            )

        except Exception:
            logger.exception(
                "No se pudo completar %s.",
                titulo,
            )
            break

        nuevos = resultado["messages"][cantidad_previa:]

        for mensaje in nuevos:
            if isinstance(mensaje, AIMessage):
                for llamada in mensaje.tool_calls:
                    print("Herramienta:", llamada["name"])
                    print("Argumentos:", llamada["args"])

            elif isinstance(mensaje, ToolMessage):
                print("Observación:", mensaje.content)

        print(
            "Respuesta:",
            StrOutputParser().invoke(
                resultado["messages"][-1]
            ),
        )

    print("\n=== HISTORIALES GUARDADOS ===")

    for config in [config_1, config_2]:
        mensajes = (
            agente.get_state(config).values.get("messages", [])
        )
        preguntas = [
            mensaje.content
            for mensaje in mensajes
            if mensaje.type == "human"
        ]

        print("Sesión:", config["configurable"]["thread_id"])
        print("Cantidad de mensajes:", len(mensajes))
        print("Mensajes del usuario:", preguntas)