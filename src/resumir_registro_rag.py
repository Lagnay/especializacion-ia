import argparse
import json
from pathlib import Path

from src.registro_rag import RUTA_REGISTRO


TARIFAS = {
    "modelo": "gemini-3.5-flash-lite",
    "modalidad": "Standard, nivel de pago",
    "unidad": "USD por millón de tokens",
    "fecha_consulta": "2026-11-12",
    "fuente": "https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite",
    "entrada": 0.30,
    "salida": 2.50,
    "cache": 0.03,
}


def estimar_costo_generacion(registro):
    modelo = registro["configuracion"]["modelo_generacion"]
    if modelo != TARIFAS["modelo"]:
        raise ValueError(f"No hay tarifas configuradas para {modelo}.")

    tokens = registro["tokens"]
    if tokens is None:
        return None

    entrada = tokens["input_tokens"]
    salida = tokens["output_tokens"]
    cache = (tokens.get("input_token_details") or {}).get("cache_read", 0)

    if any(
        isinstance(valor, bool) or not isinstance(valor, int) or valor < 0
        for valor in (entrada, salida, cache)
    ):
        raise ValueError("Los conteos deben ser enteros no negativos.")

    if cache > entrada:
        raise ValueError("Los tokens en caché superan los tokens de entrada.")

    return (
        (entrada - cache) * TARIFAS["entrada"]
        + cache * TARIFAS["cache"]
        + salida * TARIFAS["salida"]
    ) / 1_000_000


def formatear_costo(costo):
    return "N/D" if costo is None else f"{costo:.9f}"


def leer_registros(ruta):
    return [
        json.loads(linea)
        for linea in ruta.read_text(encoding="utf-8-sig").splitlines()
        if linea.strip()
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Resume tiempos y costo de referencia de generación."
    )
    parser.add_argument(
        "registro",
        nargs="?",
        type=Path,
        default=RUTA_REGISTRO,
    )
    args = parser.parse_args()

    try:
        registros = leer_registros(args.registro)
        costos = [estimar_costo_generacion(r) for r in registros]
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"No se pudo preparar el resumen: {error}\n")

    print("Registros:", len(registros))
    print("Tarifas de referencia:", TARIFAS["fecha_consulta"])
    print("Modalidad:", TARIFAS["modalidad"])
    print("Alcance: generación; costo de embeddings no calculado.")
    print()

    for registro, costo in zip(registros, costos, strict=True):
        tokens = registro["tokens"] or {}

        print(
            f"{registro['caso_id']} | k={registro['k']} | "
            f"entrada={tokens.get('input_tokens', 'N/D')} | "
            f"salida={tokens.get('output_tokens', 'N/D')} | "
            f"total={registro['tiempo_total_ms']:.2f} ms | "
            f"USD={formatear_costo(costo)}"
        )

    calculados = [costo for costo in costos if costo is not None]
    total = sum(calculados) if calculados else None

    print(
        f"\nTotal de generación estimado: "
        f"{formatear_costo(total)} USD"
    )
    print("Registros sin datos de consumo:", len(costos) - len(calculados))
    print("Importes de referencia; no acreditan un cargo real.")


if __name__ == "__main__":
    main()