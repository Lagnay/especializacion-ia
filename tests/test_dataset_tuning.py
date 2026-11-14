import json

import pytest
from google.genai import types

from src.dataset_tuning import (
    CATEGORIAS,
    MINIMO_EJEMPLOS,
    PREFIJO_ENTRADA,
    construir_dataset,
    contar_categorias,
    validar_dataset,
)


@pytest.fixture
def dataset():
    return construir_dataset()


def test_dataset_preparado_es_valido_y_no_se_modifica(dataset):
    originales = [ejemplo.model_dump() for ejemplo in dataset]

    assert len(dataset) >= MINIMO_EJEMPLOS
    assert validar_dataset(dataset) == []

    balance = contar_categorias(dataset)
    assert set(balance) == CATEGORIAS
    assert sum(balance.values()) == len(dataset)
    assert [ejemplo.model_dump() for ejemplo in dataset] == originales


@pytest.mark.parametrize(
    "output,fragmento_error",
    [
        (None, "output vacío"),
        ("   ", "output vacío"),
        ("no es JSON", "JSON válido"),
        ("[]", "únicamente categoria"),
        ("{}", "únicamente categoria"),
        ('{"categoria": "queja", "prioridad": "alta"}', "únicamente categoria"),
        ('{"categoria": []}', "categoría no permitida"),
        ('{"categoria": "otra"}', "categoría no permitida"),
        ('{"categoria": "Queja"}', "categoría no permitida"),
    ],
)
def test_rechaza_outputs_invalidos(dataset, output, fragmento_error):
    dataset[0] = types.TuningExample(
        text_input=dataset[0].text_input,
        output=output,
    )

    problemas = validar_dataset(dataset)

    assert len(problemas) == 1
    assert fragmento_error in problemas[0]


@pytest.mark.parametrize(
    "entrada,fragmento_error",
    [
        (None, "entrada vacía"),
        ("   ", "entrada vacía"),
        ("Mensaje sin instrucción.", "falta la instrucción"),
        (PREFIJO_ENTRADA + "   ", "mensaje vacío"),
    ],
)
def test_rechaza_entradas_invalidas(dataset, entrada, fragmento_error):
    dataset[0] = types.TuningExample(
        text_input=entrada,
        output=dataset[0].output,
    )

    problemas = validar_dataset(dataset)

    assert len(problemas) == 1
    assert fragmento_error in problemas[0]


def test_detecta_duplicados_con_mayusculas_y_espacios(dataset):
    mensaje = dataset[0].text_input[len(PREFIJO_ENTRADA):]

    duplicado = types.TuningExample(
        text_input=PREFIJO_ENTRADA + "  " + mensaje.upper().replace(" ", "  "),
        output=dataset[0].output,
    )

    problemas = validar_dataset(dataset + [duplicado])

    assert len(problemas) == 1
    assert "mensaje duplicado" in problemas[0]


def test_exige_el_minimo_aunque_haya_cobertura():
    pocos = [
        types.TuningExample(
            text_input=PREFIJO_ENTRADA + f"Mensaje de prueba para {categoria}.",
            output=json.dumps({"categoria": categoria}),
        )
        for categoria in sorted(CATEGORIAS)
    ]

    problemas = validar_dataset(pocos)

    assert len(problemas) == 1
    assert f"al menos {MINIMO_EJEMPLOS}" in problemas[0]


def test_detecta_categoria_ausente(dataset):
    sin_quejas = [
        ejemplo
        for ejemplo in dataset
        if json.loads(ejemplo.output)["categoria"] != "queja"
    ]

    assert validar_dataset(sin_quejas) == [
        "Categorías sin ejemplos válidos: queja"
    ]


def test_ejemplos_invalidos_no_cuentan_para_cobertura(dataset):
    alterados = [
        types.TuningExample(
            text_input=PREFIJO_ENTRADA,
            output=ejemplo.output,
        )
        if json.loads(ejemplo.output)["categoria"] == "queja"
        else ejemplo
        for ejemplo in dataset
    ]

    problemas = validar_dataset(alterados)

    assert any("mensaje vacío" in problema for problema in problemas)
    assert "Categorías sin ejemplos válidos: queja" in problemas