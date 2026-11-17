import time

from langchain_core.runnables import RunnableLambda

from src.logging_rag import procesar_consulta, registrar_evento
from src.registro_prompts import huella_prompt
from src.registro_rag import medir
from src.resumir_registro_rag import TARIFAS, estimar_costo_generacion


def obtener_prompt_aprobado(app, config, registro):
    snapshot = app.get_state(config)
    estado = snapshot.values

    if (
        snapshot.next
        or snapshot.interrupts
        or estado.get("aprobado") is not True
        or estado.get("resultado") != "activada_en_estado_local"
        or not estado.get("huella_activa")
        or estado.get("huella_activa")
        != estado.get("huella_propuesta")
    ):
        raise PermissionError(
            "La solicitud no tiene una versión aprobada y finalizada."
        )

    for version in registro.versiones:
        if (
            version["nombre"] == estado["nombre_prompt"]
            and version["huella"] == estado["huella_activa"]
        ):
            if huella_prompt(version["texto"]) != version["huella"]:
                raise ValueError(
                    "El texto aprobado no coincide con su huella."
                )

            return version

    raise ValueError(
        "La versión aprobada no está en el registro recibido."
    )


def ejecutar_servicio(
    pregunta,
    recuperar,
    modelo,
    *,
    app_supervision,
    config_supervision,
    registro,
    origen,
    modelo_generacion=None,
):
    if (
        modelo_generacion is not None
        and modelo_generacion != TARIFAS["modelo"]
    ):
        raise ValueError(
            "No hay tarifas de referencia para el modelo indicado."
        )

    inicio = time.perf_counter()
    tiempos = {}

    version = obtener_prompt_aprobado(
        app_supervision,
        config_supervision,
        registro,
    )

    def recuperar_medido(texto):
        try:
            with medir(tiempos, "recuperacion"):
                return list(recuperar(texto))
        finally:
            registrar_evento(
                "latencia_etapa",
                etapa="recuperacion",
                duracion_ms=tiempos["recuperacion"] * 1000,
            )

    def generar_medido(mensajes):
        try:
            with medir(tiempos, "generacion"):
                return modelo.invoke(mensajes)
        finally:
            registrar_evento(
                "latencia_etapa",
                etapa="generacion",
                duracion_ms=tiempos["generacion"] * 1000,
            )

    resultado = procesar_consulta(
        pregunta,
        recuperar_medido,
        RunnableLambda(generar_medido),
        origen=origen,
        instruccion_sistema=version["texto"],
        exigir_citas=True,
    )

    resultado["prompt_huella"] = version["huella"]
    resultado["tiempos_ms"] = {
        etapa: segundos * 1000
        for etapa, segundos in tiempos.items()
    }
    resultado["suma_etapas_ms"] = sum(tiempos.values()) * 1000
    resultado["modelo_generacion"] = modelo_generacion
    resultado["costo_generacion_usd"] = None
    resultado["tarifas_referencia"] = None
    resultado["alcance_costo"] = (
        "Estimación de generación; no incluye embeddings "
        "ni acredita un cargo real."
    )

    if modelo_generacion is not None:
        resultado["tarifas_referencia"] = dict(TARIFAS)
        resultado["costo_generacion_usd"] = estimar_costo_generacion({
            "configuracion": {
                "modelo_generacion": modelo_generacion,
            },
            "tokens": resultado["tokens"],
        })

    resultado["tiempo_total_ms"] = (
        time.perf_counter() - inicio
    ) * 1000

    return resultado