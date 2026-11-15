import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from .practica_supervision_interrupt import (
    construir_grafo,
    resolver_solicitud,
)


RUTA_BASE = (
    Path(__file__).resolve().parents[5]
    / "checkpoints/supervision_practica.sqlite"
)


def main():
    parser = argparse.ArgumentParser(
        description="Práctica local de supervisión persistida en SQLite."
    )
    parser.add_argument(
        "accion",
        choices=["crear", "ver", "aprobar", "rechazar"],
    )
    parser.add_argument("--solicitud", default="demo-sqlite-01")
    parser.add_argument("--version", default="v2_ejemplo")
    parser.add_argument("--base", type=Path, default=RUTA_BASE)
    args = parser.parse_args()

    if args.accion != "crear" and not args.base.is_file():
        parser.error(
            "La base no existe. Ejecuta primero la acción crear."
        )

    args.base.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "configurable": {
            "thread_id": args.solicitud,
        }
    }

    with closing(
        sqlite3.connect(str(args.base), check_same_thread=False)
    ) as conexion:
        checkpointer = SqliteSaver(
            conexion,
            serde=JsonPlusSerializer(allowed_msgpack_modules=[]),
        )
        app = construir_grafo(checkpointer=checkpointer)
        snapshot = app.get_state(config)

        if args.accion == "crear":
            if snapshot.values:
                parser.error(
                    "La solicitud ya existe. Usa otro identificador "
                    "con --solicitud."
                )

            app.invoke(
                {
                    "version_propuesta": args.version,
                    "aprobado": None,
                    "resultado": "pendiente",
                },
                config=config,
            )
            snapshot = app.get_state(config)
            print("Solicitud creada:", args.solicitud)

        elif not snapshot.values:
            parser.error(
                "No existe esa solicitud en esta base."
            )

        elif args.accion in ("aprobar", "rechazar"):
            try:
                resolver_solicitud(
                    app,
                    config,
                    version_esperada=args.version,
                    aprobar=args.accion == "aprobar",
                )
            except (TypeError, ValueError) as error:
                parser.error(str(error))

            snapshot = app.get_state(config)

        print("Base:", args.base.resolve())
        print("Solicitud:", args.solicitud)
        print("Estado:", snapshot.values)
        print("Nodo pendiente:", snapshot.next)

        if snapshot.interrupts:
            print(
                "Revisión pendiente:",
                snapshot.interrupts[0].value,
            )


if __name__ == "__main__":
    main()