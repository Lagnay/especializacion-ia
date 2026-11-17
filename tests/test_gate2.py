import json
import logging
import sqlite3
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from src import componentes_servicio_rag as componentes
from src import logging_rag as rag
from src.corpus_rag import fragmentar_corpus
from src.grafo_supervision import (
    construir_grafo,
    crear_solicitud,
    resolver_solicitud,
)
from src.registro_prompts import construir_registro_laboratorio
from src.servicio_rag import ejecutar_servicio


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    monkeypatch.setattr(
        componentes,
        "RUTA_SIMULADA",
        tmp_path / "indice",
    )

    logger = logging.Logger("gate2_prueba")
    monkeypatch.setattr(rag, "logger", logger)
    ruta_log = tmp_path / "trazas.jsonl"
    rag.configurar_logger(ruta_log)

    registro = construir_registro_laboratorio()
    version = registro.ultima("instrucciones_rag")
    config = {
        "configurable": {"thread_id": "gate2-prueba"}
    }

    try:
        with closing(
            sqlite3.connect(
                str(tmp_path / "supervision.sqlite"),
                check_same_thread=False,
            )
        ) as conexion:
            app = construir_grafo(
                registro,
                checkpointer=SqliteSaver(
                    conexion,
                    serde=JsonPlusSerializer(
                        allowed_msgpack_modules=[]
                    ),
                ),
            )

            pendiente = crear_solicitud(
                app,
                config,
                nombre_prompt=version["nombre"],
                huella_propuesta=version["huella"],
            )

            yield SimpleNamespace(
                app=app,
                config=config,
                registro=registro,
                version=version,
                pendiente=pendiente,
                ruta_log=ruta_log,
            )
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()


def aprobar(entorno):
    return resolver_solicitud(
        entorno.app,
        entorno.config,
        huella_esperada=entorno.version["huella"],
        aprobar=True,
    )


def consultar(entorno, pregunta=componentes.PREGUNTA_ENSAYO):
    with componentes.abrir_componentes_simulados() as datos:
        recuperar, modelo, _ = datos

        return ejecutar_servicio(
            pregunta,
            recuperar,
            modelo,
            app_supervision=entorno.app,
            config_supervision=entorno.config,
            registro=entorno.registro,
            origen="simulado",
        )


def leer_eventos(entorno):
    return [
        json.loads(linea)
        for linea in entorno.ruta_log.read_text(
            encoding="utf-8"
        ).splitlines()
        if linea.strip()
    ]


def test_1_pipeline_completo_reutiliza_el_indice(entorno):
    aprobar(entorno)
    primero = consultar(entorno)
    segundo = consultar(entorno)

    assert primero["estado"] == segundo["estado"] == "completada"
    assert primero["trace_id"] != segundo["trace_id"]
    assert primero["n_recuperados"] == len(fragmentar_corpus())

    indices = [
        e["datos"]
        for e in leer_eventos(entorno)
        if e["evento"] == "indice_disponible"
    ]

    assert [i["estado_indice"] for i in indices] == [
        "creado",
        "reutilizado",
    ]
    assert all(
        i["fragmentos"] == len(fragmentar_corpus())
        for i in indices
    )


def test_2_respuesta_incluye_referencia_y_fuente(entorno):
    aprobar(entorno)
    resultado = consultar(entorno)

    assert resultado["fuentes_citadas"]

    for numero, fuente in resultado["fuentes_citadas"].items():
        assert f"[{numero}]" in resultado["respuesta"]
        assert fuente == "src/cliente.py"

    assert resultado["prompt_huella"] == entorno.version["huella"]


def test_3_logs_sin_consulta_ni_documentos_crudos(
    entorno, capsys
):
    aprobar(entorno)
    correo = "cliente@example.com"
    pregunta = (
        componentes.PREGUNTA_ENSAYO
        + " Mi correo es "
        + correo
    )
    resultado = consultar(entorno, pregunta)

    archivo = entorno.ruta_log.read_text(encoding="utf-8")
    consola = capsys.readouterr().out

    contenidos = [
        pregunta,
        correo,
        resultado["respuesta"],
        *[d.page_content for d in fragmentar_corpus()],
    ]

    for contenido in contenidos:
        assert contenido not in archivo
        assert contenido not in consola

    eventos = leer_eventos(entorno)

    assert eventos
    assert {e["trace_id"] for e in eventos} == {
        resultado["trace_id"]
    }
    assert {e["origen"] for e in eventos} == {"simulado"}


def test_4_supervision_pausa_aprueba_y_rechaza(entorno):
    assert entorno.pendiente.get("__interrupt__")
    assert entorno.app.get_state(entorno.config).next == (
        "supervisar",
    )

    aprobado = aprobar(entorno)

    assert aprobado["huella_activa"] == entorno.version["huella"]
    assert not entorno.app.get_state(entorno.config).next

    rechazo = {
        "configurable": {
            "thread_id": "gate2-rechazo-prueba",
        }
    }
    pausado = crear_solicitud(
        entorno.app,
        rechazo,
        nombre_prompt=entorno.version["nombre"],
        huella_propuesta=entorno.version["huella"],
    )

    assert pausado.get("__interrupt__")

    final = resolver_solicitud(
        entorno.app,
        rechazo,
        huella_esperada=entorno.version["huella"],
        aprobar=False,
    )

    assert final["resultado"] == "rechazada"
    assert final["huella_activa"] is None
    assert not entorno.app.get_state(rechazo).next

    recuperar = Mock()
    modelo = Mock()

    with pytest.raises(PermissionError):
        ejecutar_servicio(
            componentes.PREGUNTA_ENSAYO,
            recuperar,
            modelo,
            app_supervision=entorno.app,
            config_supervision=rechazo,
            registro=entorno.registro,
            origen="simulado",
        )

    recuperar.assert_not_called()
    modelo.invoke.assert_not_called()