import argparse
import os

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from src.trazas_agente import extraer_acciones, registrar_traza
from src.herramientas_pedidos import consultar_pedido_detallado
from src.herramientas_supervisadas import simular_reembolso
from src.herramientas_tienda import consultar_stock


def construir_agente_supervisado(modelo):
    return create_agent(
        model=modelo,
        tools=[
            consultar_stock,
            consultar_pedido_detallado,
            simular_reembolso,
        ],
        system_prompt=(
            "Eres un asistente de una tienda ficticia. "
            "Consulta existencias con consultar_stock y pedidos "
            "con consultar_pedido_con_historial. "
            "Utiliza incluir_historial=True cuando lo soliciten. "
            "Puedes recuperar del contexto el pedido mencionado. "
            "Si falta un identificador o un monto necesario, "
            "pídelo sin inventarlo. "
            "Solo solicita simular_reembolso cuando el usuario "
            "pida explícitamente esa simulación e indique el monto. "
            "El monto debe ser un entero positivo en pesos. "
            "La herramienta solicita aprobación humana por consola; "
            "no puedes conceder esa aprobación tú mismo. "
            "Si devuelve no_autorizado, informa que no se ejecutó "
            "y no vuelvas a intentarlo por iniciativa propia. "
            "Si devuelve simulado, aclara que fue una simulación "
            "y que no se movió dinero. "
            "No afirmes que una acción se completó si la herramienta "
            "no lo confirma. "
            "Responde en español y de forma breve."
        ),
        checkpointer=InMemorySaver(),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Demostración del agente con supervisión humana."
    )
    parser.add_argument(
        "--ejecutar",
        action="store_true",
        help="Realiza consultas a Gemini.",
    )
    parser.add_argument(
        "--caso",
        choices=["stock", "reembolso"],
        default="stock",
    )
    argumentos = parser.parse_args()

    if not argumentos.ejecutar:
        print("Modo de preparación: no se ejecutaron consultas.")
        print("Añade --ejecutar y elige --caso stock o reembolso.")
        parser.exit()

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Falta configurar GEMINI_API_KEY.")

    nombre_modelo = "gemini-3.5-flash-lite"

    modelo = ChatGoogleGenerativeAI(
        model=nombre_modelo,
        api_key=api_key,
        vertexai=False,
        timeout=30,
        max_retries=0,
    )

    agente = construir_agente_supervisado(modelo)

    entradas = {
        "stock": "¿Cuántas unidades de arroz quedan?",
        "reembolso": (
            "Simula un reembolso de 1500 pesos "
            "para el pedido P-301."
        ),
    }

    entrada = entradas[argumentos.caso]
    session_id = f"ensayo_{uuid4().hex}"

    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 12,
    }

    print("Entrada:", entrada)

    resultado = agente.invoke(
        {"messages": [{"role": "user", "content": entrada}]},
        config=config,
    )

    acciones = extraer_acciones(resultado["messages"])
    respuesta = StrOutputParser().invoke(
        resultado["messages"][-1]
    )

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "origen": "agente_con_modelo",
        "modelo_configurado": nombre_modelo,
        "caso": argumentos.caso,
        "entrada": entrada,
        "acciones": acciones,
        "respuesta_final": respuesta,
    }

    ruta = Path(
        "docs/modulo_02/unidad_2_4/bloque_23/"
        "trazas_agente.jsonl"
    )
    registrar_traza(registro, ruta)

    print("\n=== TRAZA ===")
    for accion in acciones:
        print("Herramienta:", accion["herramienta"])
        print("Argumentos:", accion["argumentos"])
        print("Observación:", accion["observacion"])
        print("Estado:", accion["estado"])

    print("\nRespuesta:", respuesta)
    print("Traza guardada en:", ruta.resolve())