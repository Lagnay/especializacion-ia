import pytest

from src.pipeline_texto import (
    procesar_texto,
    vectorizar,
    calcular_coincidencia,
)


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")

    assert resultado == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto("¡¡¡...!!!")

    assert resultado == []


def test_procesar_texto_conserva_tildes_y_numeros():
    resultado = procesar_texto("El niño tiene 3 lápices.")

    assert resultado == ["el", "niño", "tiene", "3", "lápices"]


@pytest.mark.parametrize("entrada", [42, None])
def test_procesar_texto_rechaza_entradas_no_textuales(entrada):
    with pytest.raises(TypeError):
        procesar_texto(entrada)


def test_vectorizar_cuenta_repeticiones():
    resultado = vectorizar(["el", "gato", "el"])

    assert resultado == {"el": 2, "gato": 1}


def test_coincidencia_cambia_al_normalizar():
    referencia = "El cielo es azul."
    respuesta = "el cielo es azul"

    coincidencia_cruda = calcular_coincidencia(
        referencia.split(),
        respuesta.split(),
    )
    coincidencia_procesada = calcular_coincidencia(
        procesar_texto(referencia),
        procesar_texto(respuesta),
    )

    assert coincidencia_cruda == pytest.approx(0.5)
    assert coincidencia_procesada == pytest.approx(1.0)


def test_coincidencia_referencia_vacia_devuelve_cero():
    resultado = calcular_coincidencia([], ["hola"])

    assert resultado == 0.0