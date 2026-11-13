import json
from unittest.mock import Mock, call, patch

import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from src.registro_rag import guardar_registro, main, medir, registrar_consulta


@pytest.fixture
def componentes():
    servicios = Mock()

    servicios.embeddings.embed_query.return_value = [0.1, 0.2]

    servicios.indice.similarity_search_by_vector.return_value = [
        Document(
            id="fragmento-001",
            page_content="El cliente permite hasta tres intentos.",
            metadata={"fuente": "src/cliente.py"},
        )
    ]

    return servicios


@pytest.mark.parametrize(
    "tokens",
    [
        {"input_tokens": 100, "output_tokens": 8, "total_tokens": 108},
        None,
    ],
)
def test_registro_coordina_etapas_y_conserva_consumo(componentes, tokens):
    componentes.modelo.invoke.return_value = AIMessage(
        content=[{"type": "text", "text": "Hasta tres intentos [1]."}],
        usage_metadata=tokens,
    )

    with patch(
        "src.registro_rag.time.perf_counter",
        side_effect=range(8),
    ):
        registro = registrar_consulta(
            "¿Cuántos intentos permite?",
            componentes.embeddings,
            componentes.indice,
            componentes.modelo,
            k=2,
        )

    assert componentes.mock_calls == [
        call.embeddings.embed_query("¿Cuántos intentos permite?"),
        call.indice.similarity_search_by_vector([0.1, 0.2], k=2),
        call.modelo.invoke(registro["prompt"]),
    ]

    assert registro["k"] == 2
    assert registro["tokens"] == tokens
    assert registro["respuesta"] == "Hasta tres intentos [1]."
    assert registro["ids_recuperados"] == ["fragmento-001"]
    assert registro["fuentes_contexto"] == {1: "src/cliente.py"}

    assert "¿Cuántos intentos permite?" in registro["prompt"]
    assert "[1] El cliente permite hasta tres intentos." in registro["prompt"]
    assert "no tienes información suficiente" in registro["prompt"]

    assert registro["tiempos_ms"] == pytest.approx(
        {
            "embed_query": 1000,
            "busqueda_vectorial": 1000,
            "generacion": 1000,
        }
    )
    assert registro["suma_etapas_ms"] == pytest.approx(3000)
    assert registro["tiempo_total_ms"] == pytest.approx(7000)

    assert json.loads(json.dumps(registro))["tokens"] == tokens


@pytest.mark.parametrize(
    "pregunta,k,error",
    [
        (None, 3, TypeError),
        ("", 3, ValueError),
        ("   ", 3, ValueError),
        ("Pregunta", 0, ValueError),
        ("Pregunta", -1, ValueError),
        ("Pregunta", True, ValueError),
        ("Pregunta", 1.5, ValueError),
    ],
)
def test_entrada_invalida_no_ejecuta_etapas(componentes, pregunta, k, error):
    with pytest.raises(error):
        registrar_consulta(
            pregunta,
            componentes.embeddings,
            componentes.indice,
            componentes.modelo,
            k=k,
        )

    assert componentes.mock_calls == []


def test_fallo_embedding_no_busca_ni_genera(componentes):
    componentes.embeddings.embed_query.side_effect = ConnectionError(
        "Fallo de embedding simulado."
    )

    with pytest.raises(ConnectionError, match="embedding simulado"):
        registrar_consulta(
            "Pregunta",
            componentes.embeddings,
            componentes.indice,
            componentes.modelo,
        )

    componentes.indice.similarity_search_by_vector.assert_not_called()
    componentes.modelo.invoke.assert_not_called()


def test_fallo_busqueda_no_genera(componentes):
    componentes.indice.similarity_search_by_vector.side_effect = RuntimeError(
        "Fallo de búsqueda simulado."
    )

    with pytest.raises(RuntimeError, match="búsqueda simulado"):
        registrar_consulta(
            "Pregunta",
            componentes.embeddings,
            componentes.indice,
            componentes.modelo,
        )

    componentes.modelo.invoke.assert_not_called()


def test_medicion_conserva_duracion_si_el_bloque_falla():
    tiempos = {}

    with patch(
        "src.registro_rag.time.perf_counter",
        side_effect=[10, 10.5],
    ):
        with pytest.raises(RuntimeError, match="Fallo simulado"):
            with medir(tiempos, "etapa_fallida"):
                raise RuntimeError("Fallo simulado")

    assert tiempos["etapa_fallida"] == pytest.approx(0.5)


def test_guardado_agrega_lineas_sin_borrar_registros(tmp_path):
    ruta = tmp_path / "evidencias" / "registros.jsonl"
    primero = {"caso_id": "prueba_1", "respuesta": "Primera\nsegunda"}
    segundo = {"caso_id": "prueba_2", "tokens": None}

    guardar_registro(primero, ruta)
    contenido_anterior = ruta.read_bytes()
    guardar_registro(segundo, ruta)

    assert ruta.read_bytes().startswith(contenido_anterior)

    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert len(lineas) == 2
    assert [json.loads(linea) for linea in lineas] == [primero, segundo]


def test_guardado_invalido_conserva_el_archivo(tmp_path):
    ruta = tmp_path / "registros.jsonl"
    guardar_registro({"caso_id": "prueba"}, ruta)
    contenido_anterior = ruta.read_bytes()

    with pytest.raises(ValueError):
        guardar_registro({"tiempo_total_ms": float("nan")}, ruta)

    assert ruta.read_bytes() == contenido_anterior


def test_preparacion_no_construye_clientes_ni_guarda(
    monkeypatch, tmp_path, capsys
):
    construir = Mock()
    guardar = Mock()
    ruta = tmp_path / "no_crear" / "registros.jsonl"

    monkeypatch.setattr("src.registro_rag.construir_componentes", construir)
    monkeypatch.setattr("src.registro_rag.guardar_registro", guardar)
    monkeypatch.setattr("src.registro_rag.RUTA_REGISTRO", ruta)

    with patch("sys.argv", ["registro_rag", "--caso", "R01", "--k", "3"]):
        main()

    construir.assert_not_called()
    guardar.assert_not_called()
    assert not ruta.parent.exists()
    assert "Modo de preparación" in capsys.readouterr().out