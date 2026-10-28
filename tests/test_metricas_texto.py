import pytest

from src.metricas_texto import (
    contar_coincidencias,
    calcular_metricas,
    resumir_metricas,
)


def test_contar_coincidencias_limita_las_repeticiones():
    referencia = ["el", "gato"]
    respuesta = ["el", "gato", "el", "gato"]

    resultado = contar_coincidencias(referencia, respuesta)

    assert resultado == 2


def test_calcular_metricas_procesa_textos_y_calcula_resultados():
    referencia = "El gato duerme en el sofá."
    respuesta = "El gato duerme en el sillón todo el día."

    resultado = calcular_metricas(referencia, respuesta)

    esperado = {
        "precision": 5 / 9,
        "cobertura": 5 / 6,
        "f1": 2 / 3,
    }

    assert resultado == pytest.approx(esperado)


@pytest.mark.parametrize(
    "referencia, respuesta",
    [
        ("", ""),
        ("El gato duerme.", ""),
        ("", "El gato duerme."),
        ("gato", "perro"),
    ],
)
def test_calcular_metricas_sin_coincidencias_devuelve_ceros(
    referencia,
    respuesta,
):
    resultado = calcular_metricas(referencia, respuesta)

    assert resultado == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }


def test_resumir_metricas_calcula_promedios_por_caso():
    resultados = [
        {"precision": 1.0, "cobertura": 0.5, "f1": 2 / 3},
        {"precision": 0.5, "cobertura": 1.0, "f1": 2 / 3},
    ]

    resumen = resumir_metricas(resultados)

    assert resumen == pytest.approx({
        "precision_promedio": 0.75,
        "cobertura_promedio": 0.75,
        "f1_promedio": 2 / 3,
    })


def test_resumir_metricas_sin_resultados_devuelve_ceros():
    resumen = resumir_metricas([])

    assert resumen == {
        "precision_promedio": 0.0,
        "cobertura_promedio": 0.0,
        "f1_promedio": 0.0,
    }