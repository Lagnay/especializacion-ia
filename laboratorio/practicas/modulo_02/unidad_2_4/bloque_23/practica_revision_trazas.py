import json
from pathlib import Path


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


if __name__ == "__main__":
    print("=== CASOS SIMULADOS DEL DETECTOR ===")

    escenarios = [
        ["consultar_stock"],
        ["consultar_stock", "consultar_stock"],
        ["consultar_stock", "consultar_pedido_con_historial"],
        [
            "consultar_stock",
            "consultar_pedido_con_historial",
            "consultar_stock",
        ],
    ]

    for nombres in escenarios:
        acciones = [
            {"herramienta": nombre}
            for nombre in nombres
        ]

        print(nombres, "->", hay_repeticion_consecutiva(acciones))

    print("\n=== REVISIÓN DEL ARCHIVO GUARDADO ===")

    revisar_trazas(Path(
        "docs/modulo_02/unidad_2_4/bloque_23/"
        "trazas_supervision.jsonl"
    ))