from google.genai import types


if __name__ == "__main__":
    print("=== CAMPOS DEL SDK INSTALADO ===")

    nombres = (
        "tuning_dataset_example_count",
        "total_truncated_example_count",
        "truncated_example_indices",
        "dropped_example_reasons",
        "total_billable_token_count",
        "tuning_step_count",
    )

    for nombre in nombres:
        campo = types.SupervisedTuningDataStats.model_fields[nombre]
        print(f"{nombre}: {campo.description}")

    print("\n=== ESTADÍSTICAS SIMULADAS ===")

    # Valores ficticios para practicar su lectura.
    estadisticas = types.SupervisedTuningDataStats(
        tuning_dataset_example_count=8,
        total_truncated_example_count=1,
        truncated_example_indices=[3],
        dropped_example_reasons=["Demasiados tokens: motivo simulado."],
        total_billable_token_count=1540,
        tuning_step_count=35,
    )

    print(
        "Ejemplos en el dataset:",
        estadisticas.tuning_dataset_example_count,
    )
    print(
        "Ejemplos descartados:",
        estadisticas.total_truncated_example_count,
    )
    print(
        "Muestra de índices afectados:",
        estadisticas.truncated_example_indices,
    )
    print("Motivos:", estadisticas.dropped_example_reasons)
    print(
        "Tokens facturables:",
        estadisticas.total_billable_token_count,
    )
    print("Pasos de entrenamiento:", estadisticas.tuning_step_count)

    print("\nLectura local terminada. No se consultó ningún trabajo real.")