from unittest.mock import Mock, call

import pytest
from langchain_core.documents import Document

from src.casos_recuperacion import CASOS_RECUPERACION
from src.evaluar_recuperacion import evaluar_recuperacion


def test_evaluacion_calcula_resultados_y_promedios():
    casos = [
        CASOS_RECUPERACION[0],   # R01: un relevante.
        CASOS_RECUPERACION[10],  # R11: dos relevantes.
        CASOS_RECUPERACION[11],  # R12: ninguno relevante.
    ]

    documentos = [
        Document(id=identificador, page_content="Texto simulado.")
        for identificador in (
            "fragmento-001",
            "fragmento-004",
            "fragmento-006",
        )
    ]
    recuperar = Mock(return_value=documentos)

    informe = evaluar_recuperacion(casos, recuperar, k=3)

    assert informe["k"] == 3
    assert len(informe["resultados"]) == 3

    assert informe["promedios"]["precision"] == pytest.approx(2 / 9)
    assert informe["promedios"]["recall"] == pytest.approx(0.75)
    assert informe["promedios"]["f1"] == pytest.approx(0.45)

    resultado_sin_respuesta = informe["resultados"][2]
    assert resultado_sin_respuesta["precision"] == 0.0
    assert resultado_sin_respuesta["recall"] is None
    assert resultado_sin_respuesta["f1"] is None

    assert recuperar.call_args_list == [
        call(caso["pregunta"], k=3)
        for caso in casos
    ]


def test_evaluacion_sin_casos_no_consulta_ni_inventa_promedios():
    recuperar = Mock()

    informe = evaluar_recuperacion([], recuperar)

    assert informe["resultados"] == []
    assert informe["promedios"] == {
        "precision": None,
        "recall": None,
        "f1": None,
    }
    recuperar.assert_not_called()


@pytest.mark.parametrize("k", [0, -1])
def test_evaluacion_rechaza_k_invalido_sin_consultar(k):
    recuperar = Mock()

    with pytest.raises(ValueError, match="al menos 1"):
        evaluar_recuperacion(
            CASOS_RECUPERACION,
            recuperar,
            k=k,
        )

    recuperar.assert_not_called()