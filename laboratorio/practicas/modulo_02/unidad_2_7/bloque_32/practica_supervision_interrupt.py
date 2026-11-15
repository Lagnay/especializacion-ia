from typing import TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class Estado(TypedDict):
    version_propuesta: str
    aprobado: bool | None
    resultado: str


def proponer(estado: Estado):
    print("Versión propuesta:", estado["version_propuesta"])
    return {}


def supervisar(estado: Estado):
    decision = interrupt({
        "accion": "activar_prompt_simulado",
        "version_propuesta": estado["version_propuesta"],
    })

    if not isinstance(decision, bool):
        raise TypeError("La decisión debe ser True o False.")

    return {"aprobado": decision}


def aplicar(estado: Estado):
    resultado = (
        "activacion_simulada"
        if estado["aprobado"] is True
        else "rechazada"
    )

    return {"resultado": resultado}


def construir_grafo(checkpointer=None):
    grafo = StateGraph(Estado)

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


def resolver_solicitud(app, config, *, version_esperada, aprobar):
    if not isinstance(aprobar, bool):
        raise TypeError("La decisión debe ser True o False.")

    snapshot = app.get_state(config)

    if not snapshot.next or not snapshot.interrupts:
        raise ValueError(
            "La solicitud no tiene una aprobación pendiente."
        )

    if snapshot.values["version_propuesta"] != version_esperada:
        raise ValueError(
            "La versión pendiente no coincide con la versión revisada."
        )

    return app.invoke(Command(resume=aprobar), config=config)


if __name__ == "__main__":
    app = construir_grafo()

    for decision in (True, False):
        titulo = (
            "APROBACIÓN SIMULADA"
            if decision
            else "RECHAZO SIMULADO"
        )
        print(f"\n=== {titulo} ===")

        config = {
            "configurable": {
                "thread_id": "solicitud-" + uuid4().hex,
            }
        }

        pendiente = app.invoke(
            {
                "version_propuesta": "v2_ejemplo",
                "aprobado": None,
                "resultado": "pendiente",
            },
            config=config,
        )

        snapshot = app.get_state(config)

        print("Hay interrupción:", bool(pendiente.get("__interrupt__")))
        print("Nodo pendiente:", snapshot.next)
        print("Solicitud:", snapshot.interrupts[0].value)
        print("Resultado antes de decidir:", snapshot.values["resultado"])

        final = resolver_solicitud(
            app,
            config,
            version_esperada="v2_ejemplo",
            aprobar=decision,
        )

        print("Decisión guardada:", final["aprobado"])
        print("Resultado después de decidir:", final["resultado"])

    print("\n=== SOLICITUD YA RESUELTA ===")

    try:
        resolver_solicitud(
            app,
            config,
            version_esperada="v2_ejemplo",
            aprobar=True,
        )
    except ValueError as error:
        print("Reintento bloqueado:", error)