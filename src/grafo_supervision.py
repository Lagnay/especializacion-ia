import json
from copy import deepcopy
from typing import TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from src.registro_prompts import (
    construir_registro_laboratorio,
    huella_prompt,
)


class EstadoSupervision(TypedDict):
    nombre_prompt: str
    huella_propuesta: str
    huella_activa: str | None
    aprobado: bool | None
    resultado: str


def construir_grafo(registro, checkpointer=None):
    catalogo = {
        (version["nombre"], version["huella"]): version
        for version in registro.versiones
    }

    def buscar_version(nombre, huella):
        version = catalogo.get((nombre, huella))

        if version is None:
            raise ValueError("La versión no está registrada.")

        if huella_prompt(version["texto"]) != huella:
            raise ValueError("El texto no coincide con su huella.")

        return deepcopy(version)

    def proponer(estado):
        buscar_version(
            estado["nombre_prompt"],
            estado["huella_propuesta"],
        )

        if estado["huella_activa"] is not None:
            buscar_version(
                estado["nombre_prompt"],
                estado["huella_activa"],
            )

        return {}

    def supervisar(estado):
        version = buscar_version(
            estado["nombre_prompt"],
            estado["huella_propuesta"],
        )

        decision = interrupt({
            "accion": "activar_prompt_en_estado_local",
            "nombre": version["nombre"],
            "huella": version["huella"],
            "texto": version["texto"],
            "nota": version["nota"],
            "validacion": version["validacion"],
        })

        if not isinstance(decision, bool):
            raise TypeError("La decisión debe ser True o False.")

        return {"aprobado": decision}

    def aplicar(estado):
        buscar_version(
            estado["nombre_prompt"],
            estado["huella_propuesta"],
        )

        if estado["aprobado"] is True:
            return {
                "huella_activa": estado["huella_propuesta"],
                "resultado": "activada_en_estado_local",
            }

        return {"resultado": "rechazada"}

    grafo = StateGraph(EstadoSupervision)

    grafo.add_node("proponer", proponer)
    grafo.add_node("supervisar", supervisar)
    grafo.add_node("aplicar", aplicar)

    grafo.add_edge(START, "proponer")
    grafo.add_edge("proponer", "supervisar")
    grafo.add_edge("supervisar", "aplicar")
    grafo.add_edge("aplicar", END)

    if checkpointer is None:
        checkpointer = InMemorySaver()

    return grafo.compile(checkpointer=checkpointer)


def crear_solicitud(
    app,
    config,
    *,
    nombre_prompt,
    huella_propuesta,
    huella_activa=None,
):
    if app.get_state(config).values:
        raise ValueError(
            "Usa un thread_id nuevo para cada solicitud."
        )

    return app.invoke(
        {
            "nombre_prompt": nombre_prompt,
            "huella_propuesta": huella_propuesta,
            "huella_activa": huella_activa,
            "aprobado": None,
            "resultado": "pendiente",
        },
        config=config,
    )


def resolver_solicitud(
    app, config, *, huella_esperada, aprobar
):
    if not isinstance(aprobar, bool):
        raise TypeError("La decisión debe ser True o False.")

    snapshot = app.get_state(config)

    if not snapshot.next or not snapshot.interrupts:
        raise ValueError("No hay una aprobación pendiente.")

    if snapshot.values["huella_propuesta"] != huella_esperada:
        raise ValueError(
            "La huella no coincide con la versión revisada."
        )

    return app.invoke(Command(resume=aprobar), config=config)


if __name__ == "__main__":
    registro = construir_registro_laboratorio()
    propuesta = registro.ultima("instrucciones_rag")
    app = construir_grafo(registro)

    config = {
        "configurable": {
            "thread_id": "prompt-" + uuid4().hex,
        }
    }

    pendiente = crear_solicitud(
        app,
        config,
        nombre_prompt=propuesta["nombre"],
        huella_propuesta=propuesta["huella"],
    )
    snapshot = app.get_state(config)

    print(
        "Hay interrupción:",
        bool(pendiente.get("__interrupt__")),
    )
    print(
        "Resultado antes de decidir:",
        snapshot.values["resultado"],
    )
    print(
        "Huella activa antes:",
        snapshot.values["huella_activa"],
    )

    print("\n=== SOLICITUD PARA REVISAR ===")
    print(json.dumps(
        snapshot.interrupts[0].value,
        ensure_ascii=False,
        indent=2,
    ))

    decision = input(
        "\n¿Aprobar esta versión? [s/n]: "
    ).strip().lower()

    if decision not in {"s", "n"}:
        raise SystemExit(
            "Respuesta inválida: no se resolvió la solicitud."
        )

    final = resolver_solicitud(
        app,
        config,
        huella_esperada=propuesta["huella"],
        aprobar=decision == "s",
    )

    print("Decisión guardada:", final["aprobado"])
    print("Resultado:", final["resultado"])
    print("Huella activa:", final["huella_activa"])
    print("Este ejercicio no modifica el prompt del flujo RAG.")