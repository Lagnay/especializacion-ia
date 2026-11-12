import pytest

from src.metricas_recuperacion import calcular_metricas_recuperacion


@pytest.mark.parametrize(
    "recuperados,relevantes,esperado",
    [
        (
            ["fragmento-001", "fragmento-004", "fragmento-002"],
            {"fragmento-001", "fragmento-002"},
            {"precision": 2 / 3, "recall": 1.0, "f1": 0.8},
        ),
        (
            ["fragmento-004"],
            {"fragmento-001"},
            {"precision": 0.0, "recall": 0.0, "f1": 0.0},
        ),
        (
            [],
            {"fragmento-001"},
            {"precision": 0.0, "recall": 0.0, "f1": 0.0},
        ),
        (
            ["fragmento-004"],
            set(),
            {"precision": 0.0, "recall": None, "f1": None},
        ),
        (
            [],
            set(),
            {"precision": 0.0, "recall": None, "f1": None},
        ),
    ],
)
def test_metricas_recuperacion_calcula_resultados(
    recuperados,
    relevantes,
    esperado,
):
    resultado = calcular_metricas_recuperacion(recuperados, relevantes)

    for campo, valor_esperado in esperado.items():
        if valor_esperado is None:
            assert resultado[campo] is None
        else:
            assert resultado[campo] == pytest.approx(valor_esperado)


def test_metricas_recuperacion_rechaza_identificadores_repetidos():
    with pytest.raises(ValueError, match="no deben repetirse"):
        calcular_metricas_recuperacion(
            ["fragmento-001", "fragmento-001"],
            {"fragmento-001"},
        )