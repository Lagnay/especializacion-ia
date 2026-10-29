import json
from datetime import datetime
from pathlib import Path
from src.cliente import consultar_modelo
from src.pipeline_texto import (
    procesar_texto,
    calcular_coincidencia,
)
from src.metricas_texto import calcular_metricas
from src.casos_evaluacion import CASOS_ORIGINALES


INSTRUCCION = (
    "Responde en español, con una sola oración breve "
    "y sin formato Markdown."
)


CASOS = CASOS_ORIGINALES


if __name__ == "__main__":
    completados = 0
    fecha = datetime.now().astimezone()
    resultados = []
    errores = []

    for numero, caso in enumerate(CASOS, start=1):
        print(f"\n=== CASO {numero} ===")
        print("Consulta:", caso["consulta"])
        print("Referencia:", caso["referencia"])

        try:
            respuesta = consultar_modelo(
                caso["consulta"],
                system_instruction=INSTRUCCION,
            )

            referencia = caso["referencia"]

            coincidencia_cruda = calcular_coincidencia(
                referencia.split(),
                respuesta.split(),
            )

            tokens_referencia = procesar_texto(referencia)
            tokens_respuesta = procesar_texto(respuesta)

            coincidencia_procesada = calcular_coincidencia(
                tokens_referencia,
                tokens_respuesta,
            )

            print("Respuesta original:", respuesta)
            print("Tokens de referencia:", tokens_referencia)
            print("Tokens de respuesta:", tokens_respuesta)
            print(
                f"Coincidencia texto crudo: "
                f"{coincidencia_cruda:.1%}"
            )
            print(
                f"Coincidencia texto procesado: "
                f"{coincidencia_procesada:.1%}"
            )

            metricas = calcular_metricas(referencia, respuesta)

            print(f"Precisión: {metricas['precision']:.2f}")
            print(f"Cobertura: {metricas['cobertura']:.2f}")
            print(f"F1: {metricas['f1']:.2f}")

            resultados.append({
                "consulta": caso["consulta"],
                "referencia": referencia,
                "respuesta": respuesta,
                "precision": metricas["precision"],
                "cobertura": metricas["cobertura"],
                "f1": metricas["f1"],
            })

            completados += 1

        except (TypeError, ValueError, RuntimeError) as error:
            print("No se pudo completar el caso:", error)

            errores.append({
                "consulta": caso["consulta"],
                "referencia": caso["referencia"],
                "error": str(error),
            })

    print(f"\nCasos completados: {completados}/{len(CASOS)}")

    registro = {
        "fecha": fecha.isoformat(timespec="seconds"),
        "modelo_configurado": "gemini-3.5-flash-lite",
        "instruccion_sistema": INSTRUCCION,
        "resultados": resultados,
        "errores": errores,
    }

    carpeta = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "Bloque 16"
    )
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre = (
        f"resultados_metricas_"
        f"{fecha.strftime('%Y%m%d_%H%M%S_%f')}.json"
    )
    ruta = carpeta / nombre

    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(
            registro,
            archivo,
            indent=2,
            ensure_ascii=False,
        )

    print("\nRegistro guardado en:", ruta)