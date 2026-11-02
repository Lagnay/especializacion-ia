import pytest
import logging

from langchain_core.runnables import RunnableLambda
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from src.enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
    construir_flujo_atencion,
    RESPUESTA_RESPALDO_QUEJA,
    construir_cadena_queja_segura,
    RESPUESTA_ERROR_GENERAL,
    procesar_mensaje_seguro,
)


@pytest.mark.parametrize(
    "categoria,ruta_esperada",
    [
        ("queja", "queja"),
        ("sugerencia", "sugerencia"),
        ("pregunta", "pregunta"),
        ("desconocida", "desconocida"),
        ("queja urgente", "desconocida"),
        ("", "desconocida"),
    ],
)
def test_enrutamiento_selecciona_solo_la_ruta_esperada(
    categoria,
    ruta_esperada,
):
    mensaje = "Mensaje de prueba para verificar el enrutamiento."

    clasificacion_falsa = MagicMock(
        return_value=categoria
    )

    rutas = {
        "queja": MagicMock(
            return_value="Respuesta de queja"
        ),
        "sugerencia": MagicMock(
            return_value="Respuesta de sugerencia"
        ),
        "pregunta": MagicMock(
            return_value="Respuesta de pregunta"
        ),
        "desconocida": MagicMock(
            return_value="Respuesta de aclaración"
        ),
    }

    cadena = construir_cadena_con_enrutamiento(
        clasificacion_falsa,
        rutas,
    )

    clasificacion_falsa.assert_not_called()

    for ruta in rutas.values():
        ruta.assert_not_called()

    resultado = cadena.invoke({
        "mensaje": mensaje,
    })

    assert resultado == {
        "mensaje": mensaje,
        "categoria": categoria,
        "respuesta": rutas[ruta_esperada].return_value,
    }

    clasificacion_falsa.assert_called_once_with({
        "mensaje": mensaje,
    })

    rutas[ruta_esperada].assert_called_once_with({
        "mensaje": mensaje,
        "categoria": categoria,
    })

    for nombre, ruta in rutas.items():
        if nombre != ruta_esperada:
            ruta.assert_not_called()


@pytest.mark.parametrize(
    "salida_modelo,categoria_esperada",
    [
        (" Queja \n", "queja"),
        ("SUGERENCIA", "sugerencia"),
        ("pregunta.", "pregunta"),
        (" Queja . \n", "queja"),
        ("No estoy seguro", "no estoy seguro"),
        ("queja urgente", "queja urgente"),
        ("", ""),
    ],
)
def test_clasificacion_normaliza_salida_del_modelo(
    salida_modelo,
    categoria_esperada,
):
    modelo_falso = MagicMock(
        return_value=AIMessage(content=salida_modelo)
    )

    paso = construir_paso_clasificacion(modelo_falso)

    resultado = paso.invoke({
        "mensaje": "Mensaje de prueba.",
    })

    assert resultado == categoria_esperada
    modelo_falso.assert_called_once()


def test_flujo_integra_clasificacion_y_atencion_de_queja():
    mensaje = (
        "El pedido P-104 llegó con un cartón de leche faltante."
    )

    analisis_simulado = (
        "ANALISIS_SIMULADO: falta un cartón de leche."
    )
    plan_simulado = (
        "PLAN_SIMULADO: verificar el despacho."
    )
    borrador_simulado = (
        "BORRADOR_SIMULADO: es necesario revisar el faltante."
    )

    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content=" Queja.\n"),
        AIMessage(content=analisis_simulado),
        AIMessage(content=plan_simulado),
        AIMessage(content=borrador_simulado),
    ]

    flujo = construir_flujo_atencion(modelo_falso)

    modelo_falso.assert_not_called()

    resultado = flujo.invoke({
        "mensaje": mensaje,
    })

    assert modelo_falso.call_count == 4

    assert resultado == {
        "mensaje": mensaje,
        "categoria": "queja",
        "respuesta": borrador_simulado,
    }


def test_cadena_queja_usa_respaldo_y_registra_fallo(caplog):
    def fallar(datos):
        raise ConnectionError("Fallo de conexión simulado.")

    cadena = construir_cadena_queja_segura(
        RunnableLambda(fallar)
    )

    entrada = {
        "mensaje": "Falta un cartón de leche.",
        "categoria": "queja",
    }

    with caplog.at_level(logging.WARNING):
        resultado = cadena.invoke(entrada)

    assert resultado == RESPUESTA_RESPALDO_QUEJA

    assert "Fallo de conexión simulado." in caplog.text

    assert entrada == {
        "mensaje": "Falta un cartón de leche.",
        "categoria": "queja",
    }


def test_procesar_mensaje_seguro_conserva_resultado_exitoso():
    mensaje = "Necesito mi factura."

    esperado = {
        "mensaje": mensaje,
        "categoria": "pregunta",
        "respuesta": "Indica el número del pedido.",
    }

    flujo = MagicMock()
    flujo.invoke.return_value = esperado

    resultado = procesar_mensaje_seguro(flujo, mensaje)

    assert resultado == esperado

    flujo.invoke.assert_called_once_with({
        "mensaje": mensaje,
    })


def test_procesar_mensaje_seguro_controla_fallo_clasificacion(
    caplog,
):
    mensaje = "Necesito mi factura."

    clasificacion = MagicMock(
        side_effect=ConnectionError(
            "Fallo simulado de clasificación."
        )
    )

    rutas = {
        "queja": MagicMock(),
        "pregunta": MagicMock(),
        "sugerencia": MagicMock(),
        "desconocida": MagicMock(),
    }

    flujo = construir_cadena_con_enrutamiento(
        clasificacion,
        rutas,
    )

    with caplog.at_level(logging.ERROR):
        resultado = procesar_mensaje_seguro(
            flujo,
            mensaje,
        )

    assert resultado == {
        "mensaje": mensaje,
        "categoria": None,
        "respuesta": RESPUESTA_ERROR_GENERAL,
    }

    clasificacion.assert_called_once_with({
        "mensaje": mensaje,
    })

    for ruta in rutas.values():
        ruta.assert_not_called()

    assert "Fallo simulado de clasificación." in caplog.text
    assert caplog.records[-1].exc_info is not None


def test_flujo_queja_conserva_categoria_al_usar_respaldo(
    caplog,
):
    mensaje = "Falta un cartón de leche."

    modelo_falso = MagicMock(side_effect=[
        AIMessage(content="queja"),
        ConnectionError(
            "Fallo simulado durante el análisis."
        ),
    ])

    flujo = construir_flujo_atencion(modelo_falso)

    with caplog.at_level(logging.WARNING):
        resultado = procesar_mensaje_seguro(
            flujo,
            mensaje,
        )

    assert resultado == {
        "mensaje": mensaje,
        "categoria": "queja",
        "respuesta": RESPUESTA_RESPALDO_QUEJA,
    }

    assert modelo_falso.call_count == 2

    assert (
        "Fallo simulado durante el análisis."
        in caplog.text
    )

    assert (
        "No se pudo completar el flujo de atención."
        not in caplog.text
    )


@pytest.mark.parametrize(
    "categoria",
    ["pregunta", "sugerencia"],
)
def test_fallo_de_otras_rutas_llega_a_proteccion_general(
    categoria,
    caplog,
):
    mensaje = "Mensaje de prueba."

    modelo_falso = MagicMock(side_effect=[
        AIMessage(content=categoria),
        ConnectionError("Fallo simulado de la ruta."),
    ])

    flujo = construir_flujo_atencion(modelo_falso)

    with caplog.at_level(logging.ERROR):
        resultado = procesar_mensaje_seguro(
            flujo,
            mensaje,
        )

    assert resultado == {
        "mensaje": mensaje,
        "categoria": None,
        "respuesta": RESPUESTA_ERROR_GENERAL,
    }

    assert modelo_falso.call_count == 2
    assert "Fallo simulado de la ruta." in caplog.text


@pytest.mark.parametrize(
    "mensaje",
    ["", "   ", "No sé qué necesito."],
)
def test_mensaje_vacio_o_ambiguo_puede_recorrer_ruta_desconocida(
    mensaje,
):
    modelo_falso = MagicMock(
        return_value=AIMessage(content="desconocida")
    )

    flujo = construir_flujo_atencion(modelo_falso)

    resultado = procesar_mensaje_seguro(
        flujo,
        mensaje,
    )

    assert resultado["mensaje"] == mensaje
    assert resultado["categoria"] == "desconocida"

    assert (
        "¿Podrías explicar qué necesitas?"
        in resultado["respuesta"]
    )

    modelo_falso.assert_called_once()