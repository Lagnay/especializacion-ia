import json
import sys
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src import evaluar_clasificacion as evaluacion


CONFIGURACION = {"origen": "prueba_simulada"}


@pytest.fixture
def casos():
    return [
        {
            "id": "C01",
            "mensaje": "Falta un producto.",
            "categoria_esperada": "queja",
        },
        {
            "id": "C02",
            "mensaje": "Hola.",
            "categoria_esperada": "desconocida",
        },
    ]


@pytest.mark.parametrize(
    "original,normalizada,formato_correcto,categoria_correcta",
    [
        ("queja", "queja", True, True),
        (" Queja. \n", "queja", False, True),
        ("pregunta", "pregunta", True, False),
        ("queja urgente", "queja urgente", False, False),
        ("", "", False, False),
    ],
)
def test_distingue_formato_y_clasificacion(
    casos, original, normalizada, formato_correcto, categoria_correcta
):
    resultado = evaluacion.revisar_respuesta(casos[0], original)

    assert resultado["respuesta_original"] == original
    assert resultado["categoria_normalizada"] == normalizada
    assert resultado["formato_correcto"] is formato_correcto
    assert resultado["categoria_correcta"] is categoria_correcta
    assert resultado["id"] == casos[0]["id"]


def test_rechaza_respuestas_no_textuales(casos):
    with pytest.raises(TypeError, match="debe ser texto"):
        evaluacion.revisar_respuesta(casos[0], None)


def test_guarda_el_fallo_y_reanuda_sin_repetir_respuestas(tmp_path, casos):
    ruta = tmp_path / "evaluacion.json"
    consultar = Mock(
        side_effect=[" Queja. \n", ConnectionError("Fallo simulado")]
    )

    parcial = evaluacion.evaluar_lote(
        ruta, consultar, casos=casos, configuracion=CONFIGURACION
    )

    assert consultar.call_count == 2
    assert len(parcial["resultados"]) == 1
    assert parcial["errores"][0]["id"] == "C02"
    assert parcial["errores"][0]["tipo"] == "ConnectionError"
    assert json.loads(ruta.read_text(encoding="utf-8")) == parcial

    reanudar = Mock(return_value="desconocida")
    completo = evaluacion.evaluar_lote(
        ruta, reanudar, casos=casos, configuracion=CONFIGURACION
    )

    reanudar.assert_called_once_with("Hola.")
    assert [fila["id"] for fila in completo["resultados"]] == ["C01", "C02"]
    assert completo["resultados"][0] == parcial["resultados"][0]
    assert completo["errores"] == parcial["errores"]

    no_repetir = Mock(side_effect=AssertionError("No debe consultar"))
    evaluacion.evaluar_lote(
        ruta, no_repetir, casos=casos, configuracion=CONFIGURACION
    )
    no_repetir.assert_not_called()


@pytest.mark.parametrize("cambio", ["casos", "configuracion"])
def test_rechaza_cambios_sin_consultar_ni_modificar_registro(
    tmp_path, casos, cambio
):
    ruta = tmp_path / "evaluacion.json"

    evaluacion.evaluar_lote(
        ruta,
        Mock(side_effect=["queja", "desconocida"]),
        casos=casos,
        configuracion=CONFIGURACION,
    )
    contenido_anterior = ruta.read_bytes()
    nuevos_casos = [dict(caso) for caso in casos]
    nueva_configuracion = dict(CONFIGURACION)

    if cambio == "casos":
        nuevos_casos[0]["mensaje"] = "Otro mensaje."
    else:
        nueva_configuracion["version"] = 2

    consultar = Mock()

    with pytest.raises(ValueError, match="cambiaron"):
        evaluacion.evaluar_lote(
            ruta,
            consultar,
            casos=nuevos_casos,
            configuracion=nueva_configuracion,
        )

    consultar.assert_not_called()
    assert ruta.read_bytes() == contenido_anterior


@pytest.mark.parametrize("identificadores", [["C01", "C01"], ["C99"]])
def test_rechaza_identificadores_guardados_invalidos(
    tmp_path, casos, identificadores
):
    ruta = tmp_path / "evaluacion.json"
    registro = {
        "casos": casos,
        "configuracion": CONFIGURACION,
        "resultados": [{"id": valor} for valor in identificadores],
        "errores": [],
    }
    evaluacion.guardar_registro(ruta, registro)
    consultar = Mock()

    with pytest.raises(ValueError, match="identificadores"):
        evaluacion.evaluar_lote(
            ruta, consultar, casos=casos, configuracion=CONFIGURACION
        )

    consultar.assert_not_called()


def test_guardado_invalido_conserva_el_archivo_anterior(tmp_path):
    ruta = tmp_path / "evaluacion.json"
    evaluacion.guardar_registro(ruta, {"dato": "anterior"})
    contenido_anterior = ruta.read_bytes()

    with pytest.raises(ValueError):
        evaluacion.guardar_registro(ruta, {"dato": float("nan")})

    assert ruta.read_bytes() == contenido_anterior
    assert list(tmp_path.iterdir()) == [ruta]


def test_preparacion_no_construye_consulta_ni_guarda(tmp_path, monkeypatch):
    ruta = tmp_path / "evaluacion.json"
    prohibido = Mock(side_effect=AssertionError("No debe ejecutarse"))

    for nombre in ("construir_consulta", "evaluar_lote", "guardar_registro"):
        monkeypatch.setattr(evaluacion, nombre, prohibido)

    monkeypatch.setattr(
        sys, "argv", ["evaluar_clasificacion", "--registro", str(ruta)]
    )

    evaluacion.main()

    prohibido.assert_not_called()
    assert not ruta.exists()


def test_paso_original_conserva_el_texto_antes_de_normalizar():
    modelo = RunnableLambda(
        lambda entrada: AIMessage(content=" Queja. \n")
    )
    paso = evaluacion.construir_paso_clasificacion_original(modelo)

    original = paso.invoke({"mensaje": "Falta un producto."})

    assert original == " Queja. \n"
    assert evaluacion.normalizar_categoria(original) == "queja"