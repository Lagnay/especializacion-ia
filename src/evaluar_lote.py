import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from src.casos_evaluacion import CASOS_EVALUACION, preparar_consulta
from src.cliente import consultar_modelo
from src.metricas_texto import calcular_metricas


INSTRUCCION = (
    "Responde en español, con una sola oración breve "
    "y sin formato Markdown."
)


def guardar_registro(ruta: Path, registro: dict) -> None:
    """Guarda el estado actual de la evaluación."""
    ruta.parent.mkdir(parents=True, exist_ok=True)

    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(
            registro,
            archivo,
            indent=2,
            ensure_ascii=False,
        )


def evaluar_lote(ruta: Path) -> dict:
    """Ejecuta los casos pendientes y guarda el avance de cada uno."""
    if ruta.exists():
        with ruta.open("r", encoding="utf-8") as archivo:
            registro = json.load(archivo)

        if (
            registro["casos"] != CASOS_EVALUACION
            or registro["instruccion_sistema"] != INSTRUCCION
        ):
            raise ValueError(
                "El catálogo o la instrucción cambiaron. "
                "Utiliza otro archivo para una evaluación nueva."
            )
    else:
        registro = {
            "fecha": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "modelo_configurado": "gemini-3.5-flash-lite",
            "instruccion_sistema": INSTRUCCION,
            "casos": CASOS_EVALUACION,
            "resultados": [],
            "errores": [],
        }

        guardar_registro(ruta, registro)

    completados = {
        resultado["id"]
        for resultado in registro["resultados"]
    }

    pendientes = [
        caso
        for caso in CASOS_EVALUACION
        if caso["id"] not in completados
    ]

    print("Casos completados:", len(completados))
    print("Casos pendientes:", len(pendientes))

    for indice, caso in enumerate(pendientes):
        if indice > 0:
            time.sleep(5)

        print(f"\n=== {caso['id']} ===")
        consulta = preparar_consulta(caso)
        fallo = False

        registro["errores"] = [
            error
            for error in registro["errores"]
            if error["id"] != caso["id"]
        ]

        try:
            respuesta = consultar_modelo(
                consulta,
                system_instruction=INSTRUCCION,
            )

            metricas = calcular_metricas(
                caso["referencia"],
                respuesta,
            )

            registro["resultados"].append({
                "id": caso["id"],
                "tipo": caso["tipo"],
                "fecha": datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                "consulta": consulta,
                "referencia": caso["referencia"],
                "aspectos_esperados": caso["aspectos_esperados"],
                "respuesta": respuesta,
                "precision": metricas["precision"],
                "cobertura": metricas["cobertura"],
                "f1": metricas["f1"],
            })

            print("Respuesta:", respuesta)
            print(f"F1: {metricas['f1']:.3f}")

        except (TypeError, ValueError, RuntimeError) as error:
            fallo = True
            registro["errores"].append({
                "id": caso["id"],
                "consulta": consulta,
                "error": str(error),
            })

            print("No se pudo completar el caso:", error)

        guardar_registro(ruta, registro)

        if fallo:
            print("Lote detenido. El avance quedó guardado.")
            break

    print(
        "\nResultados completados:",
        len(registro["resultados"]),
        "de",
        len(CASOS_EVALUACION),
    )
    print("Registro:", ruta)

    return registro


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(
        description="Ejecuta y registra el lote de evaluación."
    )
    parser.add_argument(
        "--ejecutar",
        action="store_true",
        help="Realiza las consultas pendientes a Gemini.",
    )
    parser.add_argument(
        "--registro",
        type=Path,
        default=(
            raiz
            / "docs"
            / "Bloque 17"
            / "resultados_metricas.json"
        ),
        help="Archivo donde guardar o reanudar la evaluación.",
    )
    argumentos = parser.parse_args()

    if argumentos.ejecutar:
        try:
            registro = evaluar_lote(argumentos.registro)

        except (OSError, ValueError, KeyError, TypeError) as error:
            parser.exit(
                1,
                f"No se pudo procesar el lote: {error}\n",
            )

        if len(registro["resultados"]) != len(CASOS_EVALUACION):
            parser.exit(
                1,
                "Evaluación incompleta. Revisa el error registrado "
                "antes de reanudar.\n",
            )
    else:
        print("Casos preparados:", len(CASOS_EVALUACION))
        print("Modo de preparación: no se ejecutaron consultas.")
        print("Archivo de registro:", argumentos.registro)