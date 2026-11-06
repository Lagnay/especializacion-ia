from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import (
    FakeMessagesListChatModel,
)
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver


if __name__ == "__main__":
    modelo = FakeMessagesListChatModel(
        responses=[
            AIMessage(content="Primera respuesta simulada."),
            AIMessage(content="Segunda respuesta simulada."),
            AIMessage(content="Respuesta simulada de otra sesión."),
        ]
    )

    agente = create_agent(
        model=modelo,
        tools=[],
        checkpointer=InMemorySaver(),
    )

    config_1 = {
        "configurable": {
            "thread_id": "cliente_1",
        }
    }
    config_2 = {
        "configurable": {
            "thread_id": "cliente_2",
        }
    }

    agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Consulto el pedido P-301.",
                }
            ]
        },
        config=config_1,
    )

    agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Quiero continuar esta consulta.",
                }
            ]
        },
        config=config_1,
    )

    agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Consulto el pedido P-302.",
                }
            ]
        },
        config=config_2,
    )

    mensajes_1 = agente.get_state(config_1).values["messages"]
    mensajes_2 = agente.get_state(config_2).values["messages"]

    print("Mensajes de cliente_1:", len(mensajes_1))
    print("Mensajes de cliente_2:", len(mensajes_2))

    for nombre, mensajes in [
        ("cliente_1", mensajes_1),
        ("cliente_2", mensajes_2),
    ]:
        print("\n===", nombre, "===")

        for mensaje in mensajes:
            print(mensaje.type + ":", mensaje.content)

    assert len(mensajes_1) == 4
    assert len(mensajes_2) == 2