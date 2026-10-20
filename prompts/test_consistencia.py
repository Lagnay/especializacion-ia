import json
import time
import sys
from datetime import datetime

from prompts.banco import BANCO_DE_PROMPTS
from prompts.validacion import validar_salida
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)


if __name__ == "__main__":
    modelo = "gemini-3.5-flash-lite"
    repeticiones = 3
    pausa_segundos = 5

    nombres_solicitados = sys.argv[1:]

    nombres_disponibles = [
        prompt["nombre"] for prompt in BANCO_DE_PROMPTS
    ]

    for nombre in nombres_solicitados:
        if nombre not in nombres_disponibles:
            raise SystemExit(
                f"Prompt desconocido: {nombre}. "
                f"Opciones disponibles: {', '.join(nombres_disponibles)}"
            )

    registro = {
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "modelo_solicitado": modelo,
        "criterio": (
            "JSON interpretable como objeto, campos obligatorios, "
            "tipos, valores permitidos, límites numéricos "
            "y límite de palabras cuando corresponda. "
            "No constituye una evaluación automática "
            "de la exactitud del contenido."
        ),
        "prompts": {},
    }

    for prompt in BANCO_DE_PROMPTS:
        nombre = prompt["nombre"]

        if nombres_solicitados and nombre not in nombres_solicitados:
            continue

        exitos = 0
        resultados = []

        print(f"\n=== {nombre} ===")

        for intento in range(1, repeticiones + 1):
            detalle = {
                "intento": intento,
                "valido": False,
            }

            try:
                url, headers, body = armar_peticion(
                    prompt["ejemplo_usuario"],
                    modelo=modelo,
                    system_instruction=prompt["system_instruction"],
                    response_schema=prompt["response_schema"],
                )

                respuesta_api = enviar_peticion(url, headers, body)

                detalle["modelo_devuelto"] = respuesta_api.get(
                    "modelVersion",
                    "No informado",
                )

                texto = extraer_texto(respuesta_api)
                detalle["texto_generado"] = texto

                datos = parsear_respuesta_json(texto)
                detalle["datos_interpretados"] = datos

                validar_salida(datos, prompt)

                detalle["valido"] = True
                exitos += 1

                print(f"Intento {intento}: válido")
                print("Respuesta:", datos)

            except (TypeError, ValueError, RuntimeError, KeyError) as error:
                detalle["error"] = str(error)

                print(f"Intento {intento}: fallido")
                print("Motivo:", error)

            resultados.append(detalle)
            time.sleep(pausa_segundos)

        registro["prompts"][nombre] = {
            "instruccion": prompt["system_instruction"],
            "entrada": prompt["ejemplo_usuario"],
            "response_schema": prompt["response_schema"],
            "limites_palabras": prompt.get("limites_palabras", {}),
            "intentos": repeticiones,
            "exitos": exitos,
            "fallos": repeticiones - exitos,
            "resultados": resultados,
        }

        print(
            f"Resultado de {nombre}: "
            f"{exitos}/{repeticiones} respuestas válidas"
        )

    if nombres_solicitados:
        ruta_registro = "prompts/registro_resultados_parcial.json"
    else:
        ruta_registro = "prompts/registro_resultados.json"

    with open(
        ruta_registro,
        "w",
        encoding="utf-8",
    ) as archivo:
        json.dump(
            registro,
            archivo,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\nRegistro guardado en {ruta_registro}")
    print("El programa llegó al final.")