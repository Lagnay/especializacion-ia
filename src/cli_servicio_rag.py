import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from src.grafo_supervision import (
    construir_grafo,
    crear_solicitud,
    resolver_solicitud,
)
from src.registro_prompts import construir_registro_laboratorio
from src.servicio_rag import (
    obtener_prompt_aprobado,
    ejecutar_servicio,
)
from src.componentes_servicio_rag import (
    PREGUNTA_ENSAYO,
    abrir_componentes_simulados,
    abrir_componentes_reales,
)
from src.logging_rag import configurar_logger
from src.resumir_registro_rag import formatear_costo


RAIZ = Path(__file__).resolve().parents[1]
RUTA_BASE = RAIZ / "checkpoints/gate2.sqlite"
RUTA_LOG = (
    RAIZ
    / "docs/modulo_02/unidad_2_8/bloque_s1/trazas_servicio.jsonl"
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Ejecutable del servicio RAG del Gate 2."
    )

    acciones = parser.add_mutually_exclusive_group()
    acciones.add_argument("--simular", action="store_true")
    acciones.add_argument("--ejecutar", action="store_true")
    acciones.add_argument(
        "--aprobar-prompt",
        action="store_true",
    )
    acciones.add_argument(
        "--ver-prompt",
        action="store_true",
    )

    parser.add_argument(
        "--solicitud",
        default="gate2-prompt-01",
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=RUTA_BASE,
    )
    parser.add_argument(
        "--registro",
        type=Path,
        default=RUTA_LOG,
    )
    parser.add_argument("--pregunta", default=PREGUNTA_ENSAYO)
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args(argv)

    if not args.solicitud.strip():
        parser.error("La solicitud debe tener un identificador.")

    if args.k < 1:
        parser.error("k debe ser positivo.")

    if args.ejecutar and not args.pregunta.strip():
        parser.error("La pregunta no puede estar vacía.")

    if args.simular and args.pregunta != PREGUNTA_ENSAYO:
        parser.error(
            "El modo simulado utiliza la pregunta fija del ensayo."
        )

    try:
        registro = construir_registro_laboratorio()
        propuesta = registro.ultima("instrucciones_rag")

        if not any((
            args.aprobar_prompt,
            args.ver_prompt,
            args.simular,
            args.ejecutar,
        )):
            print(
                "Modo de preparación: sin consultas "
                "ni escritura de estados."
            )
            print("Versión propuesta:", propuesta["huella"])
            print("Base local:", args.base)
            print("Usa --aprobar-prompt para revisar una propuesta.")
            print("Usa --ver-prompt para consultar su estado.")
            print("Usa --simular para ejecutar el ensayo local aprobado.")
            print("Usa --ejecutar para consultar Gemini con el índice real.")
            return 0

        if (
            args.ver_prompt or args.simular or args.ejecutar
        ) and not args.base.is_file():
            raise FileNotFoundError(
                "Todavía no existe la base de supervisión."
            )

        if args.aprobar_prompt:
            args.base.parent.mkdir(parents=True, exist_ok=True)

        with closing(
            sqlite3.connect(
                str(args.base),
                check_same_thread=False,
            )
        ) as conexion:
            checkpointer = SqliteSaver(
                conexion,
                serde=JsonPlusSerializer(
                    allowed_msgpack_modules=[]
                ),
            )
            app = construir_grafo(
                registro,
                checkpointer=checkpointer,
            )
            config = {
                "configurable": {
                    "thread_id": args.solicitud,
                }
            }
            snapshot = app.get_state(config)

            if args.simular or args.ejecutar:
                obtener_prompt_aprobado(app, config, registro)
                logger = configurar_logger(args.registro)

                try:
                    componentes = (
                        abrir_componentes_simulados()
                        if args.simular
                        else abrir_componentes_reales(k=args.k)
                    )

                    with componentes as (
                        recuperar, modelo, informacion
                    ):
                        resultado = ejecutar_servicio(
                            args.pregunta,
                            recuperar,
                            modelo,
                            app_supervision=app,
                            config_supervision=config,
                            registro=registro,
                            origen=(
                                "simulado"
                                if args.simular
                                else "real"
                            ),
                            modelo_generacion=informacion.get(
                                "modelo_generacion"
                            ),
                        )
                finally:
                    for handler in list(logger.handlers):
                        logger.removeHandler(handler)
                        handler.close()

                print(
                    "Modo:",
                    "simulado" if args.simular else "real",
                )
                print("Índice:", informacion["estado_indice"])
                print("Fragmentos:", informacion["fragmentos"])
                print(
                    "Prompt utilizado:",
                    resultado["prompt_huella"],
                )
                print("Respuesta:", resultado["respuesta"])
                print(
                    "Fuentes citadas:",
                    resultado["fuentes_citadas"],
                )
                print("Consumo:", resultado["tokens"])
                print("Tiempos (ms):", resultado["tiempos_ms"])
                print(
                    f"Total: {resultado['tiempo_total_ms']:.2f} ms"
                )
                print(
                    "Costo de generación de referencia (USD):",
                    formatear_costo(
                        resultado["costo_generacion_usd"]
                    ),
                )

                if resultado["tarifas_referencia"] is not None:
                    print(
                        "Fecha de las tarifas:",
                        resultado["tarifas_referencia"][
                            "fecha_consulta"
                        ],
                    )

                print(resultado["alcance_costo"])
                print("Registro:", args.registro)
                return 0

            if args.aprobar_prompt:
                if not snapshot.values:
                    crear_solicitud(
                        app,
                        config,
                        nombre_prompt=propuesta["nombre"],
                        huella_propuesta=propuesta["huella"],
                    )
                    snapshot = app.get_state(config)

                if not snapshot.interrupts:
                    raise ValueError(
                        "La solicitud ya está resuelta. Usa otro "
                        "identificador para una propuesta nueva."
                    )

                revision = snapshot.interrupts[0].value
                print(json.dumps(
                    revision,
                    ensure_ascii=False,
                    indent=2,
                ))

                decision = input(
                    "¿Aprobar esta versión? [s/n]: "
                ).strip().lower()

                if decision not in {"s", "n"}:
                    print(
                        "Respuesta inválida: "
                        "la solicitud sigue pendiente."
                    )
                    return 2

                resolver_solicitud(
                    app,
                    config,
                    huella_esperada=revision["huella"],
                    aprobar=decision == "s",
                )
                snapshot = app.get_state(config)

            if not snapshot.values:
                raise ValueError("No existe esa solicitud.")

            print("Solicitud:", args.solicitud)
            print(
                "Resultado:",
                snapshot.values.get("resultado"),
            )
            print(
                "Huella activa:",
                snapshot.values.get("huella_activa"),
            )
            print("Nodo pendiente:", snapshot.next)

            if snapshot.values.get("aprobado") is True:
                version = obtener_prompt_aprobado(
                    app, config, registro
                )
                print("Prompt habilitado:", version["huella"])

            return 0

    except (OSError, sqlite3.Error, ValueError, TypeError) as error:
        print("No se pudo completar la operación:", error)
        return 2

    except (EOFError, KeyboardInterrupt):
        print(
            "\nOperación interrumpida; consulta el estado "
            "con --ver-prompt."
        )
        return 2

    except Exception as error:
        print("La operación falló:", type(error).__name__)
        print(
            "Revisa los eventos de la consulta y la configuración."
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())