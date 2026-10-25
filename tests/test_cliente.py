import pytest

import src.cliente as cliente

from unittest.mock import Mock, patch

from src.cliente import (
    enviar_peticion_clasificada,
    con_reintento,
)


@pytest.fixture(autouse=True)
def aislar_costo_total():
    with patch("src.cliente.costo_total_sesion", 0.0):
        yield


@pytest.mark.parametrize("codigo", [200, 201])
def test_enviar_peticion_exito(codigo):
    datos_simulados = {"texto": "respuesta simulada"}

    respuesta_falsa = Mock(status_code=codigo)
    respuesta_falsa.json.return_value = datos_simulados

    with patch(
        "src.cliente.requests.post",
        return_value=respuesta_falsa,
    ) as post_simulado:
        resultado = enviar_peticion_clasificada(
            "https://ejemplo.invalid",
            {},
            {"contents": [{"parts": [{"text": "Prueba"}]}]},
        )

    assert resultado == datos_simulados
    post_simulado.assert_called_once()


@pytest.mark.parametrize("codigo", [401, 403])
def test_enviar_peticion_credencial_o_permisos(codigo):
    respuesta_falsa = Mock(status_code=codigo)

    with patch(
        "src.cliente.requests.post",
        return_value=respuesta_falsa,
    ) as post_simulado:
        with pytest.raises(ValueError):
            enviar_peticion_clasificada(
                "https://ejemplo.invalid",
                {},
                {"contents": [{"parts": [{"text": "Prueba"}]}]},
            )

    post_simulado.assert_called_once()


@pytest.mark.parametrize("codigo", [429, 500, 502, 503, 504])
def test_enviar_peticion_error_reintentable(codigo):
    respuesta_falsa = Mock(status_code=codigo)

    with patch(
        "src.cliente.requests.post",
        return_value=respuesta_falsa,
    ) as post_simulado:
        with pytest.raises(TimeoutError):
            enviar_peticion_clasificada(
                "https://ejemplo.invalid",
                {},
                {"contents": [{"parts": [{"text": "Prueba"}]}]},
            )

    post_simulado.assert_called_once()


def test_con_reintento_recupera_tras_fallo_temporal():
    operacion = Mock(
        side_effect=[
            TimeoutError("Fallo temporal simulado."),
            "Respuesta correcta",
        ]
    )

    with patch("src.cliente.time.sleep") as pausa_simulada:
        resultado = con_reintento(operacion, intentos=3)

    assert resultado == "Respuesta correcta"
    assert operacion.call_count == 2
    pausa_simulada.assert_called_once()


def test_con_reintento_agota_intentos():
    error_simulado = TimeoutError("Fallo temporal persistente.")
    operacion = Mock(side_effect=error_simulado)

    with patch("src.cliente.time.sleep") as pausa_simulada:
        with pytest.raises(TimeoutError) as error_capturado:
            con_reintento(operacion, intentos=3)

    assert error_capturado.value is error_simulado
    assert operacion.call_count == 3
    assert pausa_simulada.call_count == 2


def test_con_reintento_no_reintenta_value_error():
    operacion = Mock(
        side_effect=ValueError("Configuración inválida.")
    )

    with patch("src.cliente.time.sleep") as pausa_simulada:
        with pytest.raises(ValueError):
            con_reintento(operacion, intentos=3)

    operacion.assert_called_once()
    pausa_simulada.assert_not_called()


def test_registrar_costo_calcula_importe():
    respuesta_simulada = {
        "usageMetadata": {
            "promptTokenCount": 850,
            "candidatesTokenCount": 320,
            "cachedContentTokenCount": 500,
            "thoughtsTokenCount": 80,
            "totalTokenCount": 1250,
        }
    }

    costo = cliente.registrar_costo(respuesta_simulada)

    assert costo == pytest.approx(0.00112)
    assert cliente.costo_total_sesion == pytest.approx(0.00112)


def test_registrar_costo_acumula():
    respuesta_simulada = {
        "usageMetadata": {
            "promptTokenCount": 11,
            "candidatesTokenCount": 3,
            "totalTokenCount": 14,
        }
    }

    cliente.registrar_costo(respuesta_simulada)

    assert cliente.costo_total_sesion == pytest.approx(0.0000108)

    cliente.registrar_costo(respuesta_simulada)

    assert cliente.costo_total_sesion == pytest.approx(0.0000216)


def test_consultar_modelo_convierte_timeout_agotado():
    error_simulado = TimeoutError("Intentos agotados.")

    with patch(
        "src.cliente.con_reintento",
        side_effect=error_simulado,
    ):
        with pytest.raises(RuntimeError) as error_capturado:
            cliente.consultar_modelo("Pregunta de prueba")

    assert str(error_capturado.value) == (
        "El servicio no pudo completar la consulta "
        "tras varios intentos. Intenta más tarde."
    )
    assert error_capturado.value.__cause__ is error_simulado
    assert cliente.costo_total_sesion == 0.0


def test_consultar_modelo_propaga_value_error():
    error_simulado = ValueError("Configuración inválida.")

    with patch(
        "src.cliente.con_reintento",
        side_effect=error_simulado,
    ):
        with pytest.raises(ValueError) as error_capturado:
            cliente.consultar_modelo("Pregunta de prueba")

    assert error_capturado.value is error_simulado
    assert cliente.costo_total_sesion == 0.0


def test_consultar_modelo_devuelve_texto_y_registra_costo():
    datos_simulados = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Edimburgo"}
                    ]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 11,
            "candidatesTokenCount": 3,
            "totalTokenCount": 14,
        },
    }

    with patch(
        "src.cliente.con_reintento",
        return_value=datos_simulados,
    ) as reintento_simulado:
        resultado = cliente.consultar_modelo(
            "¿Cuál es la capital de Escocia?"
        )

    assert resultado == "Edimburgo"
    assert cliente.costo_total_sesion == pytest.approx(0.0000108)
    reintento_simulado.assert_called_once()


@pytest.mark.parametrize("codigo", [400, 404])
def test_enviar_peticion_error_que_requiere_revision(codigo):
    respuesta_falsa = Mock(status_code=codigo)

    with patch(
        "src.cliente.requests.post",
        return_value=respuesta_falsa,
    ) as post_simulado:
        with pytest.raises(RuntimeError) as error_capturado:
            enviar_peticion_clasificada(
                "https://ejemplo.invalid",
                {},
                {"contents": [{"parts": [{"text": "Prueba"}]}]},
            )

    assert str(error_capturado.value) == (
        f"HTTP {codigo}: revisar la causa antes de reintentar."
    )
    post_simulado.assert_called_once()