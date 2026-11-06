import pytest
from pydantic import ValidationError

from langchain_core.language_models.fake_chat_models import (
    FakeMessagesListChatModel,
)
from langchain_core.messages import AIMessage

from src.agente_con_memoria import construir_agente_con_memoria
from src.herramientas_pedidos import consultar_pedido_detallado


class ModeloSimulado(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@pytest.mark.parametrize("incluir_historial", [False, True])
def test_herramienta_respeta_opcion_de_historial(incluir_historial):
    resultado = consultar_pedido_detallado.invoke({
        "pedido_id": " p-301 ",
        "incluir_historial": incluir_historial,
    })

    assert "Estado ficticio de P-301: en preparación." in resultado
    assert ("Historial:" in resultado) == incluir_historial


@pytest.mark.parametrize(
    "argumentos",
    [
        {},
        {
            "pedido_id": "P-301",
            "incluir_historial": "tal vez",
        },
    ],
)
def test_herramienta_rechaza_argumentos_invalidos(argumentos):
    with pytest.raises(ValidationError):
        consultar_pedido_detallado.invoke(argumentos)


def test_herramienta_controla_pedido_inexistente():
    resultado = consultar_pedido_detallado.invoke({
        "pedido_id": "P-999",
    })

    assert resultado == (
        "Pedido no encontrado en el registro ficticio."
    )


def test_agente_conserva_historial_y_separa_sesiones():
    modelo = ModeloSimulado(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "consultar_pedido_con_historial",
                        "args": {
                            "pedido_id": "P-301",
                            "incluir_historial": True,
                        },
                        "id": "consulta_1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Primera respuesta simulada."),
            AIMessage(content="Segunda respuesta simulada."),
            AIMessage(content="Respuesta de otra sesión."),
        ]
    )

    agente = construir_agente_con_memoria(modelo)

    config_1 = {
        "configurable": {"thread_id": "cliente_1"},
    }
    config_2 = {
        "configurable": {"thread_id": "cliente_2"},
    }

    agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Consulta P-301 con historial.",
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
                    "content": "Continúa mi consulta.",
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
                    "content": "Hola.",
                }
            ]
        },
        config=config_2,
    )

    mensajes_1 = agente.get_state(config_1).values["messages"]
    mensajes_2 = agente.get_state(config_2).values["messages"]

    preguntas_1 = [
        mensaje.content
        for mensaje in mensajes_1
        if mensaje.type == "human"
    ]
    preguntas_2 = [
        mensaje.content
        for mensaje in mensajes_2
        if mensaje.type == "human"
    ]

    assert preguntas_1 == [
        "Consulta P-301 con historial.",
        "Continúa mi consulta.",
    ]
    assert preguntas_2 == ["Hola."]

    assert any(
        mensaje.type == "tool"
        and "Historial: recibido -> en preparación."
        in mensaje.content
        for mensaje in mensajes_1
    )

    assert not any(
        mensaje.type == "tool"
        for mensaje in mensajes_2
    )