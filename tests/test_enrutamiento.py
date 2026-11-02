from unittest.mock import MagicMock

import pytest

from langchain_core.messages import AIMessage

from src.enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
    construir_flujo_atencion,
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