import json
from pathlib import Path
from langchain_core.messages import AIMessage, ToolMessage


def extraer_acciones(mensajes: list) -> list:
    acciones = []
    por_id = {}

    for mensaje in mensajes:
        if isinstance(mensaje, AIMessage):
            for llamada in mensaje.tool_calls:
                accion = {
                    "id_llamada": llamada["id"],
                    "herramienta": llamada["name"],
                    "argumentos": llamada["args"],
                    "observacion": None,
                    "estado": "sin_resultado",
                }
                acciones.append(accion)
                por_id[llamada["id"]] = accion

        elif isinstance(mensaje, ToolMessage):
            accion = por_id[mensaje.tool_call_id]
            observacion = mensaje.content

            if isinstance(observacion, str):
                try:
                    observacion = json.loads(observacion)
                except json.JSONDecodeError:
                    pass

            accion["observacion"] = observacion
            accion["estado"] = mensaje.status

    return acciones


def registrar_traza(registro: dict, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)

    linea = json.dumps(registro, ensure_ascii=False)

    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(linea + "\n")


def hay_repeticion_consecutiva(acciones: list) -> bool:
    for indice in range(1, len(acciones)):
        actual = acciones[indice]["herramienta"]
        anterior = acciones[indice - 1]["herramienta"]

        if actual == anterior:
            return True

    return False


def revisar_trazas(ruta: Path) -> None:
    try:
        with ruta.open(encoding="utf-8") as archivo:
            for numero, linea in enumerate(archivo, start=1):
                if not linea.strip():
                    continue

                try:
                    registro = json.loads(linea)
                except json.JSONDecodeError:
                    print(f"Línea {numero}: JSON inválido; revisar.")
                    continue

                sospechosa = hay_repeticion_consecutiva(
                    registro["acciones"]
                )

                if sospechosa:
                    print(
                        f"Línea {numero}: revisar repetición "
                        f"en sesión {registro['session_id']}."
                    )
                else:
                    print(
                        f"Línea {numero}: "
                        "sin repeticiones consecutivas."
                    )

    except FileNotFoundError:
        print("No existe el archivo de trazas:", ruta)