import pytest

from src.decision_personalizacion import (
    PREGUNTAS,
    recomendar_estrategia,
)


@pytest.mark.parametrize(
    "activas,puntos_esperados,candidatas_esperadas",
    [
        (
            (
                "problema_de_formato_o_tono",
                "dataset_grande_y_de_calidad",
            ),
            {"RAG": 0, "Fine-tuning completo": 3, "PEFT": 3},
            ["Fine-tuning completo", "PEFT"],
        ),
        (
            (
                "informacion_cambia_seguido",
                "problema_de_formato_o_tono",
                "presupuesto_limitado_o_iterar_rapido",
            ),
            {"RAG": 5, "Fine-tuning completo": 1, "PEFT": 3},
            ["RAG"],
        ),
        (
            (
                "problema_de_formato_o_tono",
                "presupuesto_limitado_o_iterar_rapido",
                "necesita_multiples_variantes",
            ),
            {"RAG": 2, "Fine-tuning completo": 1, "PEFT": 5},
            ["PEFT"],
        ),
        (
            ("dataset_grande_y_de_calidad",),
            {"RAG": 0, "Fine-tuning completo": 2, "PEFT": 1},
            ["Fine-tuning completo"],
        ),
        (
            (),
            {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0},
            ["RAG", "Fine-tuning completo", "PEFT"],
        ),
    ],
    ids=["empate", "rag", "peft", "completo", "sin_apoyo"],
)
def test_calcula_puntos_y_conserva_todas_las_candidatas(
    activas,
    puntos_esperados,
    candidatas_esperadas,
):
    respuestas = dict.fromkeys(PREGUNTAS, False)

    for clave in activas:
        respuestas[clave] = True

    puntos, candidatas = recomendar_estrategia(respuestas)

    assert puntos == puntos_esperados
    assert candidatas == candidatas_esperadas


@pytest.mark.parametrize("entrada", [None, [], "texto"])
def test_rechaza_entradas_que_no_son_diccionarios(entrada):
    with pytest.raises(TypeError, match="diccionario"):
        recomendar_estrategia(entrada)


@pytest.mark.parametrize("modo", ["falta", "extra", "sustituida"])
def test_exige_exactamente_las_cinco_preguntas(modo):
    respuestas = dict.fromkeys(PREGUNTAS, False)

    if modo in ("falta", "sustituida"):
        respuestas.pop(PREGUNTAS[0])

    if modo in ("extra", "sustituida"):
        respuestas["otra_pregunta"] = True

    with pytest.raises(ValueError, match="exactamente las cinco"):
        recomendar_estrategia(respuestas)


@pytest.mark.parametrize("valor", [None, "False", 0, 1])
def test_rechaza_valores_que_no_son_booleanos(valor):
    respuestas = dict.fromkeys(PREGUNTAS, False)
    respuestas["dataset_grande_y_de_calidad"] = valor

    with pytest.raises(TypeError, match="debe ser True o False"):
        recomendar_estrategia(respuestas)


def test_no_modifica_las_respuestas_recibidas():
    respuestas = dict.fromkeys(PREGUNTAS, True)
    originales = respuestas.copy()

    recomendar_estrategia(respuestas)

    assert respuestas == originales