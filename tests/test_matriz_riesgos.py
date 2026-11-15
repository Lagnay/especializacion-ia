import pytest

from src.matriz_riesgos import (
    categoria_riesgo,
    esta_en_el_limite,
    puntaje_riesgo,
)


@pytest.mark.parametrize(
    "probabilidad,impacto,puntaje,categoria",
    [
        (1, 1, 1, "BAJO"),
        (1, 3, 3, "BAJO"),
        (2, 2, 4, "MEDIO"),
        (2, 4, 8, "MEDIO"),
        (3, 3, 9, "ALTO"),
        (3, 4, 12, "ALTO"),
        (3, 5, 15, "CRITICO"),
        (5, 5, 25, "CRITICO"),
    ],
)
def test_calcula_puntaje_y_categoria(
    probabilidad, impacto, puntaje, categoria
):
    assert puntaje_riesgo(probabilidad, impacto) == puntaje
    assert categoria_riesgo(puntaje) == categoria


@pytest.mark.parametrize(
    "probabilidad,impacto,error",
    [
        (None, 3, TypeError),
        ("3", 3, TypeError),
        (True, 3, TypeError),
        (3, 2.5, TypeError),
        (0, 3, ValueError),
        (3, 6, ValueError),
    ],
)
def test_rechaza_escalas_invalidas(probabilidad, impacto, error):
    with pytest.raises(error):
        puntaje_riesgo(probabilidad, impacto)

    with pytest.raises(error):
        esta_en_el_limite(probabilidad, impacto)


@pytest.mark.parametrize(
    "puntaje,error",
    [
        (None, TypeError),
        (True, TypeError),
        (0, ValueError),
        (26, ValueError),
    ],
)
def test_rechaza_puntajes_invalidos(puntaje, error):
    with pytest.raises(error):
        categoria_riesgo(puntaje)


@pytest.mark.parametrize(
    "probabilidad,impacto,esperado",
    [
        (1, 1, False),
        (1, 2, True),
        (2, 4, True),
        (3, 5, True),
        (4, 5, False),
    ],
)
def test_detecta_cambio_de_categoria_al_variar_un_punto(
    probabilidad, impacto, esperado
):
    assert esta_en_el_limite(probabilidad, impacto) is esperado