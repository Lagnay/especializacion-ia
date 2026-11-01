from unittest.mock import MagicMock

from langchain_core.messages import AIMessage

from src.cadena_reclamos import construir_cadena


def test_cadena_conecta_los_tres_pasos():
    mensaje = "El pedido P-104 llegó con un cartón de leche faltante."

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
        AIMessage(content=analisis_simulado),
        AIMessage(content=plan_simulado),
        AIMessage(content=borrador_simulado),
    ]

    cadena = construir_cadena(modelo_falso)

    assert modelo_falso.call_count == 0

    resultado = cadena.invoke({"mensaje": mensaje})

    assert modelo_falso.call_count == 3
    assert isinstance(resultado, str)
    assert resultado == borrador_simulado

    llamadas = modelo_falso.call_args_list

    prompt_analisis = llamadas[0].args[0].to_string()
    prompt_planificacion = llamadas[1].args[0].to_string()
    prompt_redaccion = llamadas[2].args[0].to_string()

    assert mensaje in prompt_analisis
    assert analisis_simulado in prompt_planificacion
    assert mensaje in prompt_redaccion
    assert plan_simulado in prompt_redaccion