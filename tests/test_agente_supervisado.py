import json
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from langchain_core.language_models.fake_chat_models import (
    FakeMessagesListChatModel,
)
from langchain_core.messages import AIMessage, ToolMessage

import src.herramientas_supervisadas as herramientas
from src.agente_supervisado import construir_agente_supervisado
from src.trazas_agente import extraer_acciones


class ModeloSimulado(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


@pytest.fixture
def entorno_supervisado(monkeypatch, tmp_path):
    ruta = tmp_path / "aprobaciones.jsonl"
    aprobacion = Mock(return_value=True)

    monkeypatch.setattr(
        herramientas, "RUTA_APROBACIONES", ruta
    )
    monkeypatch.setattr(
        herramientas, "esperar_aprobacion", aprobacion
    )

    return ruta, aprobacion


@pytest.mark.parametrize(
    "aprobado, estado",
    [
        (True, "simulado"),
        (False, "no_autorizado"),
    ],
)
def test_reembolso_respeta_y_registra_decision(
    entorno_supervisado, aprobado, estado
):
    ruta, aprobacion = entorno_supervisado
    aprobacion.return_value = aprobado

    resultado = herramientas.simular_reembolso.invoke({
        "numero_pedido": "P-301",
        "monto": 1500,
    })

    assert resultado["estado"] == estado
    assert resultado["aprobacion"]["aprobado"] is aprobado
    aprobacion.assert_called_once()

    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert len(lineas) == 1

    decision = json.loads(lineas[0])
    assert decision == resultado["aprobacion"]
    assert decision["argumentos"] == {
        "numero_pedido": "P-301",
        "monto": 1500,
    }


@pytest.mark.parametrize(
    "monto", [1500.5, 1500.0, 0, -100, True]
)
def test_monto_invalido_no_pide_aprobacion_ni_registra(
    entorno_supervisado, monto
):
    ruta, aprobacion = entorno_supervisado

    with pytest.raises(ValidationError):
        herramientas.simular_reembolso.invoke({
            "numero_pedido": "P-301",
            "monto": monto,
        })

    aprobacion.assert_not_called()
    assert not ruta.exists()


def test_fallo_de_registro_interrumpe_la_herramienta(
    entorno_supervisado, monkeypatch
):
    registro_fallido = Mock(
        side_effect=OSError("Fallo de escritura simulado.")
    )
    monkeypatch.setattr(
        herramientas, "registrar_traza", registro_fallido
    )

    with pytest.raises(OSError, match="Fallo de escritura"):
        herramientas.simular_reembolso.invoke({
            "numero_pedido": "P-301",
            "monto": 1500,
        })

    registro_fallido.assert_called_once()


@pytest.mark.parametrize("aprobado", [True, False])
def test_agente_recibe_resultado_y_decision_de_la_herramienta(
    entorno_supervisado, aprobado
):
    ruta, aprobacion = entorno_supervisado
    aprobacion.return_value = aprobado

    modelo = ModeloSimulado(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "simular_reembolso",
                        "args": {
                            "numero_pedido": "P-301",
                            "monto": 1500,
                        },
                        "id": "reembolso_1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Respuesta final simulada."),
        ]
    )

    agente = construir_agente_supervisado(modelo)

    resultado = agente.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Simula un reembolso de 1500 pesos "
                        "para el pedido P-301."
                    ),
                }
            ]
        },
        config={
            "configurable": {"thread_id": "prueba_supervision"},
            "recursion_limit": 12,
        },
    )

    observaciones = [
        mensaje
        for mensaje in resultado["messages"]
        if isinstance(mensaje, ToolMessage)
    ]

    assert len(observaciones) == 1
    assert observaciones[0].tool_call_id == "reembolso_1"

    contenido = json.loads(observaciones[0].content)

    assert contenido["aprobacion"]["aprobado"] is aprobado
    assert contenido["estado"] == (
        "simulado" if aprobado else "no_autorizado"
    )

    decision = json.loads(
        ruta.read_text(encoding="utf-8").strip()
    )
    assert decision == contenido["aprobacion"]
    assert resultado["messages"][-1].content == (
        "Respuesta final simulada."
    )

    acciones = extraer_acciones(resultado["messages"])

    assert len(acciones) == 1
    assert acciones[0]["id_llamada"] == "reembolso_1"
    assert acciones[0]["herramienta"] == "simular_reembolso"
    assert acciones[0]["argumentos"] == {
        "numero_pedido": "P-301",
        "monto": 1500,
    }
    assert acciones[0]["estado"] == "success"
    assert acciones[0]["observacion"] == contenido