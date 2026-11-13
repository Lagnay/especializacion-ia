import json

import pytest

from src.resumir_registro_rag import estimar_costo_generacion, leer_registros


def crear_registro(tokens, modelo="gemini-3.5-flash-lite"):
    return {
        "configuracion": {"modelo_generacion": modelo},
        "tokens": tokens,
    }


@pytest.mark.parametrize(
    "tokens,esperado",
    [
        (
            {"input_tokens": 179, "output_tokens": 12, "total_tokens": 191},
            0.0000837,
        ),
        (
            {
                "input_tokens": 100,
                "output_tokens": 20,
                "total_tokens": 120,
                "input_token_details": {"cache_read": 40},
                "output_token_details": {"reasoning": 10},
            },
            0.0000692,
        ),
        (
            {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            0.0,
        ),
        (None, None),
    ],
)
def test_costo_generacion_calcula_sin_duplicar_consumo(tokens, esperado):
    costo = estimar_costo_generacion(crear_registro(tokens))

    if esperado is None:
        assert costo is None
    else:
        assert costo == pytest.approx(esperado)


@pytest.mark.parametrize(
    "entrada,salida,cache",
    [
        (-1, 2, 0),
        (10, True, 0),
        (10, 1.5, 0),
        (10, 2, 11),
    ],
)
def test_costo_rechaza_conteos_invalidos(entrada, salida, cache):
    tokens = {
        "input_tokens": entrada,
        "output_tokens": salida,
        "input_token_details": {"cache_read": cache},
    }

    with pytest.raises(ValueError):
        estimar_costo_generacion(crear_registro(tokens))


def test_costo_rechaza_modelo_sin_tarifa():
    tokens = {"input_tokens": 10, "output_tokens": 2}

    with pytest.raises(ValueError, match="No hay tarifas"):
        estimar_costo_generacion(
            crear_registro(tokens, modelo="otro-modelo")
        )


def test_lector_admite_bom_y_lineas_vacias_sin_modificar_archivo(tmp_path):
    ruta = tmp_path / "registros.jsonl"
    registros = [
        {"caso_id": "prueba_1", "respuesta": "Primera\nsegunda"},
        {"caso_id": "prueba_2", "tokens": None},
    ]
    contenido = "\n\n".join(
        json.dumps(registro, ensure_ascii=False)
        for registro in registros
    )
    ruta.write_text(contenido + "\n", encoding="utf-8-sig")
    contenido_anterior = ruta.read_bytes()

    assert leer_registros(ruta) == registros
    assert ruta.read_bytes() == contenido_anterior