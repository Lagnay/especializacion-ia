import json
from unittest.mock import patch

import pytest

import src.evaluar_lote as lote


@pytest.fixture
def casos_prueba():
    casos = [
        {
            "id": "P01",
            "tipo": "prueba",
            "consulta": "Responde uno.",
            "referencia": "uno",
            "aspectos_esperados": ["Responder uno."],
        },
        {
            "id": "P02",
            "tipo": "prueba",
            "consulta": "Responde dos.",
            "referencia": "dos",
            "aspectos_esperados": ["Responder dos."],
        },
    ]

    with (
        patch.object(lote, "CASOS_EVALUACION", casos),
        patch.object(lote.time, "sleep"),
    ):
        yield casos


def test_lote_guarda_las_respuestas(tmp_path, casos_prueba):
    ruta = tmp_path / "evaluacion" / "resultados.json"

    with patch.object(
        lote,
        "consultar_modelo",
        side_effect=["uno", "dos"],
    ) as consulta:
        registro = lote.evaluar_lote(ruta)

    guardado = json.loads(ruta.read_text(encoding="utf-8"))

    assert consulta.call_count == 2
    assert guardado == registro
    assert [
        resultado["respuesta"]
        for resultado in guardado["resultados"]
    ] == ["uno", "dos"]
    assert guardado["errores"] == []


def test_lote_reanuda_sin_repetir_resultados(tmp_path, casos_prueba):
    ruta = tmp_path / "resultados.json"

    with patch.object(
        lote,
        "consultar_modelo",
        side_effect=["uno", RuntimeError("Fallo simulado.")],
    ):
        lote.evaluar_lote(ruta)

    parcial = json.loads(ruta.read_text(encoding="utf-8"))

    assert len(parcial["resultados"]) == 1
    assert parcial["resultados"][0]["id"] == "P01"
    assert parcial["errores"][0]["id"] == "P02"

    primer_resultado = parcial["resultados"][0]

    with patch.object(
        lote,
        "consultar_modelo",
        return_value="dos",
    ) as consulta:
        completo = lote.evaluar_lote(ruta)

    consulta.assert_called_once_with(
        "Responde dos.",
        system_instruction=lote.INSTRUCCION,
    )
    assert len(completo["resultados"]) == 2
    assert completo["resultados"][0] == primer_resultado
    assert completo["errores"] == []
    assert json.loads(ruta.read_text(encoding="utf-8")) == completo


@pytest.mark.parametrize(
    "atributo, valor",
    [
        ("CASOS_EVALUACION", []),
        ("INSTRUCCION", "Otra instrucción."),
    ],
)
def test_lote_rechaza_configuracion_cambiada(
    tmp_path,
    casos_prueba,
    atributo,
    valor,
):
    ruta = tmp_path / "resultados.json"

    with patch.object(
        lote,
        "consultar_modelo",
        side_effect=["uno", "dos"],
    ):
        lote.evaluar_lote(ruta)

    contenido_original = ruta.read_text(encoding="utf-8")

    with (
        patch.object(lote, atributo, valor),
        patch.object(lote, "consultar_modelo") as consulta,
    ):
        with pytest.raises(
            ValueError,
            match="catálogo o la instrucción cambiaron",
        ):
            lote.evaluar_lote(ruta)

        consulta.assert_not_called()

    assert ruta.read_text(encoding="utf-8") == contenido_original