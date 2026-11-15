import sqlite3
from contextlib import closing
from uuid import uuid4

import pytest
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from src.grafo_supervision import (
    construir_grafo,
    crear_solicitud,
    resolver_solicitud,
)
from src.registro_prompts import RegistroDePrompts


def crear_registro():
    registro = RegistroDePrompts()

    for texto in ("Versión anterior.", "Versión propuesta."):
        registro.registrar(
            "rag", texto, "laboratorio", "Prueba local.",
            validacion={"tipo": "simulada"},
        )

    return registro


@pytest.fixture
def solicitud():
    registro = crear_registro()
    anterior, propuesta = registro.versiones
    app = construir_grafo(registro)
    config = {"configurable": {"thread_id": uuid4().hex}}

    crear_solicitud(
        app, config,
        nombre_prompt="rag",
        huella_propuesta=propuesta["huella"],
        huella_activa=anterior["huella"],
    )

    return app, config, anterior, propuesta


def test_pausa_antes_de_cambiar_la_version_activa(solicitud):
    app, config, anterior, propuesta = solicitud
    snapshot = app.get_state(config)

    assert snapshot.next == ("supervisar",)
    assert snapshot.values["aprobado"] is None
    assert snapshot.values["resultado"] == "pendiente"
    assert snapshot.values["huella_activa"] == anterior["huella"]

    revision = snapshot.interrupts[0].value
    assert revision["huella"] == propuesta["huella"]
    assert revision["texto"] == propuesta["texto"]
    assert revision["validacion"] == propuesta["validacion"]


@pytest.mark.parametrize("aprobar", [True, False])
def test_aprobacion_cambia_version_y_rechazo_conserva_anterior(
    solicitud, aprobar
):
    app, config, anterior, propuesta = solicitud

    final = resolver_solicitud(
        app, config,
        huella_esperada=propuesta["huella"],
        aprobar=aprobar,
    )

    esperada = propuesta if aprobar else anterior

    assert final["huella_activa"] == esperada["huella"]
    assert final["aprobado"] is aprobar
    assert final["resultado"] == (
        "activada_en_estado_local" if aprobar else "rechazada"
    )
    assert not app.get_state(config).next


@pytest.mark.parametrize("aprobar", [None, "no", 0, 1])
def test_decision_no_booleana_no_resuelve_solicitud(
    solicitud, aprobar
):
    app, config, anterior, propuesta = solicitud

    with pytest.raises(TypeError):
        resolver_solicitud(
            app, config,
            huella_esperada=propuesta["huella"],
            aprobar=aprobar,
        )

    snapshot = app.get_state(config)

    assert snapshot.interrupts
    assert snapshot.values["aprobado"] is None
    assert snapshot.values["huella_activa"] == anterior["huella"]


def test_huella_abreviada_no_autoriza_la_version(solicitud):
    app, config, anterior, propuesta = solicitud

    with pytest.raises(ValueError):
        resolver_solicitud(
            app, config,
            huella_esperada=propuesta["huella"][:12],
            aprobar=True,
        )

    snapshot = app.get_state(config)

    assert snapshot.interrupts
    assert snapshot.values["huella_activa"] == anterior["huella"]


@pytest.mark.parametrize("aprobar", [True, False])
def test_solicitud_resuelta_no_admite_otra_decision(
    solicitud, aprobar
):
    app, config, _, propuesta = solicitud

    resolver_solicitud(
        app, config,
        huella_esperada=propuesta["huella"],
        aprobar=aprobar,
    )
    estado_anterior = app.get_state(config).values

    with pytest.raises(ValueError):
        resolver_solicitud(
            app, config,
            huella_esperada=propuesta["huella"],
            aprobar=not aprobar,
        )

    assert app.get_state(config).values == estado_anterior


def test_no_sobrescribe_una_solicitud_pendiente(solicitud):
    app, config, anterior, _ = solicitud
    estado_anterior = app.get_state(config).values

    with pytest.raises(ValueError):
        crear_solicitud(
            app, config,
            nombre_prompt="rag",
            huella_propuesta=anterior["huella"],
        )

    assert app.get_state(config).values == estado_anterior
    assert app.get_state(config).interrupts


def test_no_propone_una_version_que_no_esta_registrada():
    app = construir_grafo(crear_registro())
    config = {"configurable": {"thread_id": uuid4().hex}}

    with pytest.raises(ValueError, match="no está registrada"):
        crear_solicitud(
            app, config,
            nombre_prompt="rag",
            huella_propuesta="0" * 64,
        )


def test_sqlite_recupera_la_solicitud_al_reabrir_conexion(tmp_path):
    registro = crear_registro()
    anterior, propuesta = registro.versiones
    base = tmp_path / "supervision.sqlite"
    config = {
        "configurable": {
            "thread_id": "persistencia-test",
        }
    }

    with closing(
        sqlite3.connect(str(base), check_same_thread=False)
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

        crear_solicitud(
            app, config,
            nombre_prompt="rag",
            huella_propuesta=propuesta["huella"],
            huella_activa=anterior["huella"],
        )

        assert app.get_state(config).interrupts

    with closing(
        sqlite3.connect(str(base), check_same_thread=False)
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

        snapshot = app.get_state(config)

        assert (
            snapshot.values["huella_activa"]
            == anterior["huella"]
        )
        assert (
            snapshot.interrupts[0].value["texto"]
            == propuesta["texto"]
        )

        final = resolver_solicitud(
            app, config,
            huella_esperada=propuesta["huella"],
            aprobar=True,
        )

        assert final["huella_activa"] == propuesta["huella"]
        assert not app.get_state(config).next