import argparse
import json
from pathlib import Path

from src.metricas_texto import resumir_metricas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Resume las métricas de una evaluación guardada."
    )
    parser.add_argument(
        "archivo",
        type=Path,
        help="Ruta al archivo JSON que contiene la evaluación.",
    )
    argumentos = parser.parse_args()

    try:
        with argumentos.archivo.open(
            "r",
            encoding="utf-8",
        ) as archivo:
            registro = json.load(archivo)

        resultados = registro["resultados"]
        errores = registro["errores"]

        print("Fecha de la evaluación:", registro["fecha"])
        print("Casos completados:", len(resultados))
        print("Casos con error:", len(errores))

        if resultados:
            resumen = resumir_metricas(resultados)

            print("\n=== PROMEDIOS ===")
            print(
                f"Precisión: "
                f"{resumen['precision_promedio']:.3f}"
            )
            print(
                f"Cobertura: "
                f"{resumen['cobertura_promedio']:.3f}"
            )
            print(f"F1: {resumen['f1_promedio']:.3f}")

            casos_ordenados = sorted(
                resultados,
                key=lambda caso: caso["f1"],
            )

            print("\n=== CASOS ORDENADOS POR F1 ASCENDENTE ===")

            for caso in casos_ordenados:
                print(f"\nConsulta: {caso['consulta']}")
                print("Referencia:", caso["referencia"])
                print("Respuesta:", caso["respuesta"])
                print(f"F1: {caso['f1']:.3f}")

        else:
            print("No hay resultados exitosos para resumir.")

    except (OSError, ValueError, KeyError, TypeError) as error:
        print("No se pudo procesar el registro:", error)