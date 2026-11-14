from google.genai import types


if __name__ == "__main__":
    config = types.CreateTuningJobConfig(
        tuning_mode=types.TuningMode.TUNING_MODE_PEFT_ADAPTER,
        adapter_size=types.AdapterSize.ADAPTER_SIZE_FOUR,
        epoch_count=5,
        tuned_model_display_name="practica-local-clasificador",
    )

    print("Configuración local:")
    print(config.model_dump_json(indent=2, exclude_none=True))

    print("\nCampos y descripciones del SDK:")
    for nombre in (
        "epoch_count",
        "learning_rate_multiplier",
        "batch_size",
    ):
        campo = types.CreateTuningJobConfig.model_fields[nombre]
        print(nombre, "->", campo.description)

    print("\nEstados definidos en el SDK:")
    for estado in types.JobState:
        print("-", estado.value)

    print("\nConfiguración construida localmente, sin enviar un trabajo.")