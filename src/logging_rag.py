import hashlib
import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from langchain_core.messages import AIMessage

from src.recuperacion import resolver_citas
from src.seguridad_rag import (
    INSTRUCCION_SISTEMA,
    construir_mensajes_filtrados,
)


trace_id_var = ContextVar("rag_trace_id", default=None)
origen_var = ContextVar("rag_origen", default=None)
logger = logging.getLogger("rag_instrumentado")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "ts": datetime.fromtimestamp(
                    record.created, timezone.utc
                ).isoformat(timespec="seconds"),
                "level": record.levelname,
                "evento": record.getMessage(),
                "trace_id": trace_id_var.get(),
                "origen": origen_var.get(),
                "datos": getattr(record, "extra_data", {}),
            },
            ensure_ascii=False,
            allow_nan=False,
        )


def configurar_logger(ruta=None):
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    logger.setLevel(logging.INFO)
    logger.propagate = False
    salidas = [logging.StreamHandler(sys.stdout)]

    if ruta is not None:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        salidas.append(
            logging.FileHandler(ruta, mode="a", encoding="utf-8")
        )

    for salida in salidas:
        salida.setFormatter(JsonFormatter())
        logger.addHandler(salida)

    return logger


def registrar_evento(evento, *, nivel=logging.INFO, **datos):
    logger.log(nivel, evento, extra={"extra_data": datos})


def registrar_consumo(respuesta):
    if not isinstance(respuesta, AIMessage):
        raise TypeError("El modelo debe devolver un AIMessage.")

    uso = respuesta.usage_metadata

    registrar_evento(
        "consumo_llm",
        disponible=uso is not None,
        input_tokens=uso.get("input_tokens") if uso is not None else None,
        output_tokens=uso.get("output_tokens") if uso is not None else None,
        total_tokens=uso.get("total_tokens") if uso is not None else None,
    )

    return dict(uso) if uso is not None else None


def procesar_consulta(
    pregunta,
    recuperar,
    modelo,
    *,
    origen,
    instruccion_sistema=INSTRUCCION_SISTEMA,
    exigir_citas=False,
):
    if not isinstance(exigir_citas, bool):
        raise TypeError("exigir_citas debe ser True o False.")
    if not isinstance(instruccion_sistema, str):
        raise TypeError("La instrucción de sistema debe ser texto.")
    if not instruccion_sistema.strip():
        raise ValueError(
            "La instrucción de sistema no puede estar vacía."
        )
    if not isinstance(pregunta, str):
        raise TypeError("La pregunta debe ser texto.")

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if origen not in ("simulado", "real"):
        raise ValueError("El origen debe ser simulado o real.")

    identificador = "trace-" + uuid4().hex
    token_trace = trace_id_var.set(identificador)
    token_origen = origen_var.set(origen)
    etapa = "inicio"

    try:
        registrar_evento(
            "consulta_recibida",
            pregunta_len=len(pregunta),
            prompt_huella=hashlib.sha256(
                instruccion_sistema.encode("utf-8")
            ).hexdigest(),
        )

        etapa = "recuperacion"
        registrar_evento("recuperacion_inicio")
        documentos = list(recuperar(pregunta))
        registrar_evento(
            "recuperacion_fin",
            n_documentos=len(documentos),
        )

        etapa = "filtrado"
        mensajes, citas, descartados = construir_mensajes_filtrados(
            pregunta,
            documentos,
            instruccion_sistema=instruccion_sistema,
        )

        for documento, patrones in descartados:
            registrar_evento(
                "documento_sospechoso_descartado",
                nivel=logging.WARNING,
                fuente=documento.metadata.get("fuente"),
                n_patrones=len(patrones),
                documento_sha256=hashlib.sha256(
                    documento.page_content.encode("utf-8")
                ).hexdigest(),
            )

        registrar_evento(
            "contexto_filtrado",
            n_limpios=len(citas),
            n_descartados=len(descartados),
            fuentes=list(citas.values()),
        )

        if not citas:
            estado = "sin_contexto"
            texto = (
                "No tengo información suficiente "
                "en el contexto disponible."
            )
            tokens = None

            registrar_evento(
                "generacion_omitida",
                motivo="sin_contexto_aceptado",
            )

        else:
            etapa = "generacion"
            registrar_evento("generacion_inicio")
            respuesta = modelo.invoke(mensajes)

            etapa = "consumo"
            tokens = registrar_consumo(respuesta)
            texto = str(respuesta.text)
            estado = "completada"

            registrar_evento(
                "generacion_fin",
                respuesta_len=len(texto),
            )

        etapa = "citacion"
        fuentes_citadas = resolver_citas(texto, citas)

        if exigir_citas and estado == "completada":
            if (
                not fuentes_citadas
                or any(
                    fuente is None
                    for fuente in fuentes_citadas.values()
                )
            ):
                raise ValueError(
                    "La respuesta no incluye referencias válidas "
                    "al contexto aceptado."
                )

            registrar_evento(
                "referencias_validadas",
                n_referencias=len(fuentes_citadas),
            )

        registrar_evento("consulta_fin", estado=estado)

        return {
            "trace_id": identificador,
            "origen": origen,
            "estado": estado,
            "respuesta": texto,
            "citas": citas,
            "fuentes_citadas": fuentes_citadas,
            "n_recuperados": len(documentos),
            "n_descartados": len(descartados),
            "tokens": tokens,
        }

    except Exception as error:
        registrar_evento(
            "consulta_error",
            nivel=logging.ERROR,
            etapa=etapa,
            tipo_error=type(error).__name__,
        )
        raise

    finally:
        origen_var.reset(token_origen)
        trace_id_var.reset(token_trace)