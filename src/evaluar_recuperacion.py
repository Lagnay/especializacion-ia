import argparse
import json

from datetime import datetime
from pathlib import Path

from src.metricas_recuperacion import calcular_metricas_recuperacion


def evaluar_recuperacion(casos, recuperar, k=3):
    if k < 1:
        raise ValueError("k debe ser al menos 1.")

    resultados = []

    for caso in casos:
        documentos = recuperar(caso["pregunta"], k=k)
        ids_recuperados = [documento.id for documento in documentos]

        if len(ids_recuperados) > k:
            raise ValueError("El recuperador devolvió más de k fragmentos.")

        if any(
            not isinstance(identificador, str) or not identificador
            for identificador in ids_recuperados
        ):
            raise ValueError(
                "Cada fragmento debe tener un identificador de texto."
            )

        metricas = calcular_metricas_recuperacion(
            ids_recuperados,
            caso["ids_relevantes"],
        )

        resultados.append(
            {
                "id": caso["id"],
                "pregunta": caso["pregunta"],
                "ids_relevantes": sorted(caso["ids_relevantes"]),
                "ids_recuperados": ids_recuperados,
                **metricas,
            }
        )

    promedios = {}

    for campo in ("precision", "recall", "f1"):
        valores = [
            resultado[campo]
            for resultado in resultados
            if resultado[campo] is not None
        ]

        promedios[campo] = (
            sum(valores) / len(valores)
            if valores
            else None
        )

    return {
        "k": k,
        "resultados": resultados,
        "promedios": promedios,
    }


def formatear_metrica(valor):
    return "N/D" if valor is None else f"{valor:.3f}"


def guardar_informe(informe, configuracion, carpeta):
    fecha = datetime.now().astimezone()
    nombre = f"evaluacion_{fecha:%Y%m%d_%H%M%S_%f}_k{informe['k']}"

    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_json = carpeta / f"{nombre}.json"
    ruta_txt = carpeta / f"{nombre}.txt"

    registro = {
        "fecha": fecha.isoformat(),
        "configuracion": configuracion,
        **informe,
    }

    with ruta_json.open("x", encoding="utf-8") as archivo:
        json.dump(
            registro,
            archivo,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        archivo.write("\n")

    lineas = [
        f"Fecha: {registro['fecha']}",
        f"Configuración: {json.dumps(configuracion, ensure_ascii=False)}",
        f"k: {informe['k']}",
        "",
    ]

    for resultado in informe["resultados"]:
        valores = " | ".join(
            f"{campo}={formatear_metrica(resultado[campo])}"
            for campo in ("precision", "recall", "f1")
        )
        lineas.append(
            f"{resultado['id']} | {valores} | {resultado['pregunta']}"
        )

    lineas.append("")

    for campo, valor in informe["promedios"].items():
        lineas.append(
            f"Promedio {campo}: {formatear_metrica(valor)}"
        )

    with ruta_txt.open("x", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas) + "\n")

    return ruta_json, ruta_txt


def main():
    from src.casos_recuperacion import CASOS_RECUPERACION
    from src.corpus_rag import fragmentar_corpus
    from src.indexar_corpus import (
        DIMENSIONES,
        MODELO_EMBEDDINGS,
        nombre_coleccion,
    )

    parser = argparse.ArgumentParser(
        description="Evalúa la recuperación del corpus."
    )
    parser.add_argument("--ejecutar", action="store_true")
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()

    if args.k < 1:
        parser.error("k debe ser al menos 1.")

    configuracion = {
        "coleccion": nombre_coleccion(fragmentar_corpus()),
        "modelo_embeddings": MODELO_EMBEDDINGS,
        "dimensiones": DIMENSIONES,
        "chunk_size": 240,
        "chunk_overlap": 35,
    }

    print("Casos preparados:", len(CASOS_RECUPERACION))
    print("Fragmentos por pregunta:", args.k)
    print("Colección:", configuracion["coleccion"])

    if not args.ejecutar:
        print("Modo de preparación: no se realizaron consultas.")
        print("Añade --ejecutar para evaluar el recuperador real.")
        return

    from src.recuperacion import recuperar_fragmentos

    def recuperar_con_avance(pregunta, k):
        print("\nRecuperando:", pregunta)
        return recuperar_fragmentos(pregunta, k=k)

    try:
        informe = evaluar_recuperacion(
            CASOS_RECUPERACION,
            recuperar_con_avance,
            k=args.k,
        )
    except (ConnectionError, FileNotFoundError, ValueError) as error:
        parser.exit(1, f"No se completó la evaluación: {error}\n")

    carpeta = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "modulo_02"
        / "unidad_2_5"
        / "bloque_27"
    )
    ruta_json, ruta_txt = guardar_informe(
        informe,
        configuracion,
        carpeta,
    )

    print("\n=== RESULTADOS ===")

    for resultado in informe["resultados"]:
        valores = " | ".join(
            f"{campo}={formatear_metrica(resultado[campo])}"
            for campo in ("precision", "recall", "f1")
        )
        print(f"{resultado['id']} | {valores}")

    print("\n=== PROMEDIOS ===")
    for campo, valor in informe["promedios"].items():
        print(f"{campo}: {formatear_metrica(valor)}")

    print("\nRegistro JSON:", ruta_json)
    print("Informe TXT:", ruta_txt)


if __name__ == "__main__":
    main()