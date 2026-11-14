import argparse
import inspect
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.casos_clasificacion import CASOS_CLASIFICACION
from src.enrutamiento import (
    construir_paso_clasificacion_original,
    normalizar_categoria,
)


CATEGORIAS = {"queja", "pregunta", "sugerencia", "desconocida"}
UMBRAL_FORMATO = 3

OPCIONES_MODELO = {
    "model": "gemini-3.5-flash-lite",
    "vertexai": False,
    "timeout": 30,
    "max_retries": 0,
}

RUTA_REGISTRO = (
    Path(__file__).resolve().parents[1]
    / "docs/modulo_02/unidad_2_6/bloque_30/evaluacion_clasificacion.json"
)


def configuracion_actual():
    return {
        "modelo": dict(OPCIONES_MODELO),
        "codigo_clasificador": inspect.getsource(
            construir_paso_clasificacion_original
        ),
        "codigo_normalizacion": inspect.getsource(normalizar_categoria),
        "criterio_formato": "Etiqueta exacta tras quitar espacios exteriores.",
        "categorias": sorted(CATEGORIAS),
        "umbral_incumplimientos_formato": UMBRAL_FORMATO,
    }


def revisar_respuesta(caso, original):
    if not isinstance(original, str):
        raise TypeError("La respuesta original debe ser texto.")

    normalizada = normalizar_categoria(original)

    return {
        **caso,
        "fecha": datetime.now(timezone.utc).isoformat(),
        "respuesta_original": original,
        "categoria_normalizada": normalizada,
        "formato_correcto": original.strip() in CATEGORIAS,
        "categoria_correcta": normalizada == caso["categoria_esperada"],
    }


def guardar_registro(ruta, registro):
    contenido = json.dumps(
        registro,
        ensure_ascii=False,
        indent=2,
        allow_nan=False,
    )
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = None

    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=ruta.parent,
            delete=False,
        ) as archivo:
            temporal = Path(archivo.name)
            archivo.write(contenido)

        temporal.replace(ruta)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)


def evaluar_lote(ruta, consultar, *, casos=None, configuracion=None):
    ruta = Path(ruta)

    if casos is None:
        casos = CASOS_CLASIFICACION

    if configuracion is None:
        configuracion = configuracion_actual()

    if ruta.exists():
        registro = json.loads(ruta.read_text(encoding="utf-8-sig"))

        if (
            registro["casos"] != casos
            or registro["configuracion"] != configuracion
        ):
            raise ValueError(
                "Los casos o la configuración cambiaron. "
                "Utiliza otro archivo con --registro."
            )
    else:
        registro = {
            "inicio": datetime.now(timezone.utc).isoformat(),
            "configuracion": configuracion,
            "casos": casos,
            "resultados": [],
            "errores": [],
        }
        guardar_registro(ruta, registro)

    ids_guardados = [
        resultado["id"]
        for resultado in registro["resultados"]
    ]
    ids_validos = {caso["id"] for caso in casos}

    if (
        len(ids_guardados) != len(set(ids_guardados))
        or not set(ids_guardados) <= ids_validos
    ):
        raise ValueError("El registro contiene identificadores inválidos.")

    completados = set(ids_guardados)

    print("Casos completados:", len(completados))
    print("Casos pendientes:", len(casos) - len(completados))

    for caso in casos:
        if caso["id"] in completados:
            continue

        print(f"\n=== {caso['id']} ===")

        try:
            original = consultar(caso["mensaje"])
            resultado = revisar_respuesta(caso, original)

        except Exception as error:
            registro["errores"].append({
                "id": caso["id"],
                "fecha": datetime.now(timezone.utc).isoformat(),
                "tipo": type(error).__name__,
                "detalle": str(error),
            })
            guardar_registro(ruta, registro)
            print("Lote detenido. Error registrado:", error)
            break

        registro["resultados"].append(resultado)
        guardar_registro(ruta, registro)

        print("Original:", repr(original))
        print("Normalizada:", repr(resultado["categoria_normalizada"]))
        print("Formato correcto:", resultado["formato_correcto"])
        print("Categoría correcta:", resultado["categoria_correcta"])

    return registro


def construir_consulta():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Falta configurar GEMINI_API_KEY.")

    modelo = ChatGoogleGenerativeAI(
        api_key=api_key,
        **OPCIONES_MODELO,
    )
    paso = construir_paso_clasificacion_original(modelo)

    return lambda mensaje: paso.invoke({"mensaje": mensaje})


def main():
    parser = argparse.ArgumentParser(
        description="Evalúa el formato y la categoría del clasificador."
    )
    parser.add_argument("--ejecutar", action="store_true")
    parser.add_argument(
        "--registro",
        type=Path,
        default=RUTA_REGISTRO,
    )
    args = parser.parse_args()

    print("Casos preparados:", len(CASOS_CLASIFICACION))
    print("Modelo:", OPCIONES_MODELO["model"])
    print("Registro:", args.registro)

    if not args.ejecutar:
        print(
            "Modo de preparación: sin consultas "
            "ni escritura de registros."
        )
        return

    try:
        registro = evaluar_lote(
            args.registro,
            construir_consulta(),
        )
    except Exception as error:
        parser.exit(
            1,
            f"No se pudo ejecutar o guardar el lote: {error}\n",
        )

    resultados = registro["resultados"]
    total = len(resultados)

    fallos_formato = sum(
        not resultado["formato_correcto"]
        for resultado in resultados
    )
    aciertos = sum(
        resultado["categoria_correcta"]
        for resultado in resultados
    )

    print(
        f"\nRespuestas guardadas: "
        f"{total}/{len(CASOS_CLASIFICACION)}"
    )
    print("Incumplimientos de formato:", fallos_formato)
    print("Categorías correctas:", aciertos)
    print("Registro:", args.registro.resolve())

    if total != len(CASOS_CLASIFICACION):
        parser.exit(
            1,
            "Muestra incompleta: revisa el error antes de reanudar.\n",
        )

    print(
        "Alcanza el umbral del curso:",
        fallos_formato >= UMBRAL_FORMATO,
    )


if __name__ == "__main__":
    main()