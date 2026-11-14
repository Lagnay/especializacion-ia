import json
from collections import Counter

from google.genai import types

from .practica_ejemplos_tuning import construir_ejemplos
from .practica_validacion_tuning import validar_ejemplos


def contar_categorias(ejemplos):
    return Counter(
        json.loads(ejemplo.output)["categoria"]
        for ejemplo in ejemplos
    )


if __name__ == "__main__":
    permitidas = {"red", "autenticacion", "cuota"}
    originales = construir_ejemplos()

    salida_red = json.dumps(
        {
            "categoria": "red",
            "accion_sugerida": "reintentar con backoff exponencial",
        },
        ensure_ascii=False,
    )

    adicionales = [
        types.TuningExample(text_input=texto, output=salida_red)
        for texto in (
            "ConnectionError: se interrumpió la conexión con el proveedor.",
            "TimeoutError: se agotó el tiempo de lectura de la respuesta.",
        )
    ]

    desbalanceados = originales + adicionales

    sin_cuota = [
        ejemplo
        for ejemplo in originales
        if json.loads(ejemplo.output)["categoria"] != "cuota"
    ]

    for nombre, lote in (
        ("ORIGINAL", originales),
        ("DESBALANCEADO", desbalanceados),
        ("SIN CUOTA", sin_cuota),
    ):
        problemas = validar_ejemplos(lote, permitidas)
        if problemas:
            raise ValueError("\n".join(problemas))

        balance = contar_categorias(lote)

        print(f"\n=== {nombre} ===")
        print(f"{len(lote)} ejemplos, 0 problemas de formato.")

        for categoria in sorted(permitidas):
            print(f"{categoria}: {balance[categoria]}")

        cuentas = [balance[categoria] for categoria in permitidas]
        minimo = min(cuentas)

        if minimo == 0:
            print("Hay categorías sin ejemplos; no se calcula la razón.")
        else:
            print(f"Razón max/min: {max(cuentas) / minimo:.1f}x")

    print("\nRevisión local terminada, sin entrenamiento.")