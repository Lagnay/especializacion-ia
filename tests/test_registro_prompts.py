from datetime import datetime

import pytest

from src.registro_prompts import (
    RegistroDePrompts,
    comparar_prompts,
    construir_registro_laboratorio,
    huella_prompt,
)


@pytest.mark.parametrize(
    "texto,error",
    [
        (None, TypeError),
        (42, TypeError),
        ("", ValueError),
        ("   ", ValueError),
    ],
)
def test_rechaza_prompts_invalidos_sin_registrarlos(texto, error):
    registro = RegistroDePrompts()

    with pytest.raises(error):
        registro.registrar(
            "rag", texto, "laboratorio", "Prueba.",
            validacion={},
        )

    assert registro.versiones == []


def test_registrar_conserva_copias_independientes():
    registro = RegistroDePrompts()
    validacion = {"configuracion": {"temperatura": 0}}

    devuelta = registro.registrar(
        "rag", "Texto original.", "laboratorio", "Prueba.",
        validacion=validacion,
    )

    validacion["configuracion"]["temperatura"] = 1
    devuelta["texto"] = "Texto modificado."
    devuelta["validacion"]["configuracion"]["temperatura"] = 2

    guardada = registro.ultima("rag")

    assert guardada["texto"] == "Texto original."
    assert (
        guardada["validacion"]["configuracion"]["temperatura"]
        == 0
    )

    fecha = datetime.fromisoformat(guardada["fecha"])
    assert fecha.utcoffset().total_seconds() == 0


@pytest.mark.parametrize("lectura", ["versiones", "ultima"])
def test_modificar_una_lectura_no_altera_el_registro(lectura):
    registro = RegistroDePrompts()
    registro.registrar(
        "rag", "Texto original.", "laboratorio", "Prueba.",
        validacion={"datos": {"tipo": "simulada"}},
    )

    copia = (
        registro.versiones[0]
        if lectura == "versiones"
        else registro.ultima("rag")
    )

    copia["texto"] = "Otro texto."
    copia["validacion"]["datos"]["tipo"] = "consulta_real"

    assert registro.ultima("rag")["texto"] == "Texto original."
    assert (
        registro.ultima("rag")["validacion"]["datos"]["tipo"]
        == "simulada"
    )


def test_ultima_busca_por_nombre_y_respeta_el_orden():
    registro = RegistroDePrompts()

    for nombre, texto in [
        ("rag", "Primera."),
        ("rag", "Segunda."),
        ("otro", "Tercera."),
    ]:
        registro.registrar(
            nombre, texto, "laboratorio", "Prueba.",
            validacion={},
        )

    assert registro.ultima("rag")["texto"] == "Segunda."
    assert registro.ultima("otro")["texto"] == "Tercera."
    assert registro.ultima("ausente") is None
    assert len(registro.versiones) == 3


@pytest.mark.parametrize("campo", ["nombre", "autor", "nota"])
def test_rechaza_campos_vacios_sin_registrar(campo):
    registro = RegistroDePrompts()
    argumentos = {
        "nombre": "rag",
        "texto": "Texto.",
        "autor": "laboratorio",
        "nota": "Prueba.",
        "validacion": {},
    }
    argumentos[campo] = "   "

    with pytest.raises(ValueError):
        registro.registrar(**argumentos)

    assert registro.versiones == []


@pytest.mark.parametrize("validacion", [None, []])
def test_rechaza_validacion_que_no_es_diccionario(validacion):
    registro = RegistroDePrompts()

    with pytest.raises(TypeError):
        registro.registrar(
            "rag", "Texto.", "laboratorio", "Prueba.",
            validacion=validacion,
        )

    assert registro.versiones == []


def test_huella_detecta_espacios_que_el_diff_por_palabras_omite():
    anterior = "Responde usando contexto."
    nueva = "Responde  usando contexto."

    assert huella_prompt(anterior) != huella_prompt(nueva)
    assert len(huella_prompt(anterior)) == 64
    assert comparar_prompts(anterior, nueva) == []


def test_diff_muestra_palabras_agregadas_y_retiradas():
    diferencias = comparar_prompts(
        "Responde siempre.",
        "Responde con citas.",
    )

    assert "-siempre." in diferencias
    assert "+con" in diferencias
    assert "+citas." in diferencias


def test_registro_del_laboratorio_distingue_la_evidencia():
    from src.seguridad_rag import INSTRUCCION_SISTEMA

    registro = construir_registro_laboratorio()
    anterior, actual = registro.versiones

    assert anterior["huella"] != actual["huella"]
    assert anterior["validacion"]["tipo"] == "consulta_real"
    assert anterior["validacion"]["configuracion"]["modelo_generacion"]
    assert actual["texto"] == INSTRUCCION_SISTEMA
    assert actual["validacion"]["tipo"] == "simulada"
    assert actual["validacion"]["modelo_real"] is None
    assert registro.ultima("instrucciones_rag") == actual