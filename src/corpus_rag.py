from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


CORPUS = [
    Document(
        page_content=(
            "El cliente REST permite hasta tres intentos por consulta. "
            "Los fallos de conexión, los tiempos de espera agotados y "
            "ciertos estados HTTP pueden activar un reintento.\n\n"
            "La espera crece a partir de dos segundos, incorpora una "
            "variación aleatoria y tiene un máximo de treinta segundos. "
            "Si falla el último intento, el cliente termina la operación."
        ),
        metadata={"tema": "Reintentos", "fuente": "src/cliente.py"},
    ),
    Document(
        page_content=(
            "El cliente REST interpreta HTTP 401 y 403 como problemas "
            "de credencial o permisos. Lanza un ValueError y evita "
            "reintentar la solicitud de forma automática."
        ),
        metadata={"tema": "Credenciales", "fuente": "src/cliente.py"},
    ),
    Document(
        page_content=(
            "El cliente REST calcula un costo de referencia a partir "
            "de los tokens informados por Gemini y las tarifas "
            "configuradas. Acumula ese importe durante la sesión. "
            "El resultado es una estimación del costo."
        ),
        metadata={"tema": "Costos", "fuente": "src/cliente.py"},
    ),
    Document(
        page_content=(
            "El agente con memoria conserva los mensajes durante la "
            "ejecución. Cada thread_id mantiene su propio historial y "
            "permite continuar una conversación usando el mismo agente. "
            "La memoria se pierde al terminar el proceso."
        ),
        metadata={
            "tema": "Memoria",
            "fuente": "src/agente_con_memoria.py",
        },
    ),
    Document(
        page_content=(
            "La herramienta de reembolso simulado valida un monto "
            "en pesos enteros positivos. Solicita aprobación por "
            "consola durante treinta segundos y registra la decisión. "
            "Si se rechaza o vence el plazo, la simulación queda sin autorizar."
        ),
        metadata={
            "tema": "Supervisión",
            "fuente": "src/herramientas_supervisadas.py",
        },
    ),
]


def fragmentar_corpus() -> list[Document]:
    divisor = RecursiveCharacterTextSplitter(
        chunk_size=240,
        chunk_overlap=35,
    )
    return divisor.split_documents(CORPUS)


if __name__ == "__main__":
    fragmentos = fragmentar_corpus()

    print("Documentos:", len(CORPUS))
    print("Fragmentos:", len(fragmentos))

    for numero, fragmento in enumerate(fragmentos, start=1):
        tema = fragmento.metadata["tema"]
        longitud = len(fragmento.page_content)
        print(f"{numero}. {tema} ({longitud} caracteres)")