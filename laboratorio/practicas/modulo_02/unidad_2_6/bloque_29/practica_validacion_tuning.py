import json

from google.genai import types

from .practica_ejemplos_tuning import construir_ejemplos


def validar_ejemplos(ejemplos, categorias_permitidas):
    problemas = []
    vistos = set()
    claves_esperadas = {"categoria", "accion_sugerida"}

    for numero, ejemplo in enumerate(ejemplos, start=1):
        entrada = (ejemplo.text_input or "").strip()

        if not entrada:
            problemas.append(f"Ejemplo {numero}: entrada vacía.")
        else:
            if entrada in vistos:
                problemas.append(f"Ejemplo {numero}: entrada duplicada.")
            vistos.add(entrada)

        try:
            salida = json.loads(ejemplo.output or "")
        except json.JSONDecodeError:
            problemas.append(f"Ejemplo {numero}: output no es JSON válido.")
            continue

        if not isinstance(salida, dict):
            problemas.append(f"Ejemplo {numero}: output debe ser un objeto JSON.")
            continue

        if set(salida) != claves_esperadas:
            problemas.append(
                f"Ejemplo {numero}: output debe tener exactamente "
                "categoria y accion_sugerida."
            )
            continue

        if any(
            not isinstance(valor, str) or not valor.strip()
            for valor in salida.values()
        ):
            problemas.append(
                f"Ejemplo {numero}: los campos deben ser textos no vacíos."
            )
            continue

        if salida["categoria"] not in categorias_permitidas:
            problemas.append(f"Ejemplo {numero}: categoría no permitida.")

    return problemas


if __name__ == "__main__":
    permitidas = {"red", "autenticacion", "cuota"}
    ejemplos = construir_ejemplos()

    ejemplos_con_errores = ejemplos + [
        types.TuningExample(
            text_input="",
            output='{"categoria": "red"}',
        ),
        types.TuningExample(
            text_input=ejemplos[0].text_input,
            output="no es JSON",
        ),
        types.TuningExample(
            text_input="Entrada adicional uno.",
            output="[]",
        ),
        types.TuningExample(
            text_input="Entrada adicional dos.",
            output=json.dumps(
                {"categoria": "otra", "accion_sugerida": "revisar el caso"}
            ),
        ),
    ]

    for nombre, lote in (
        ("ORIGINAL", ejemplos),
        ("CON ERRORES", ejemplos_con_errores),
    ):
        problemas = validar_ejemplos(lote, permitidas)
        print(f"\n=== {nombre} ===")
        print(f"{len(lote)} ejemplos, {len(problemas)} problemas.")

        for problema in problemas:
            print("-", problema)

    print("\nValidación local terminada, sin entrenamiento.")