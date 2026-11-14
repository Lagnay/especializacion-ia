import json
from collections import Counter

from google.genai import types


CATEGORIAS = {"queja", "sugerencia", "pregunta", "desconocida"}

MINIMO_EJEMPLOS = 10

INSTRUCCION_TAREA = (
    "Clasifica la intención principal del mensaje de un cliente de una tienda. "
    "queja: informa un problema concreto o incumplimiento y busca atención, "
    "aunque lo formule como pregunta. "
    "sugerencia: propone una mejora sin informar un problema concreto que requiera atención. "
    "pregunta: solicita información sin plantear un problema concreto ni una mejora. "
    "desconocida: saludo, agradecimiento o información insuficiente para identificar una intención. "
    "Si combina un problema concreto con una mejora, prioriza queja. "
    "Devuelve únicamente un objeto JSON con la clave categoria y uno de estos valores: "
    "queja, sugerencia, pregunta, desconocida."
)

PREFIJO_ENTRADA = f"{INSTRUCCION_TAREA}\n\nMensaje:\n"

# Mensajes ficticios redactados para el ejercicio.
EJEMPLOS_RAW = [
    (
        "Queja urgente: compré dos cartones de leche y recibí uno.",
        "queja",
    ),
    (
        "¿Por qué me cobraron dos veces el pedido P-410?",
        "queja",
    ),
    (
        "El pedido debía llegar el martes y todavía no lo recibo. Necesito ayuda con la entrega.",
        "queja",
    ),
    (
        "El paquete llegó roto; deberían reforzar el embalaje.",
        "queja",
    ),
    (
        "Me gustaría poder elegir la franja horaria al comprar.",
        "sugerencia",
    ),
    (
        "Sería útil recibir un aviso cuando el pedido salga a reparto.",
        "sugerencia",
    ),
    (
        "Propongo que el catálogo permita filtrar productos sin lactosa.",
        "sugerencia",
    ),
    (
        "¿Podrían agregar una lista para guardar mis productos favoritos?",
        "sugerencia",
    ),
    (
        "¿Qué información debo enviar para solicitar la factura?",
        "pregunta",
    ),
    (
        "¿Cómo puedo consultar el estado de un pedido?",
        "pregunta",
    ),
    (
        "¿Se puede pagar mediante transferencia bancaria?",
        "pregunta",
    ),
    (
        "Quisiera saber qué tamaños de paquetes de arroz ofrecen.",
        "pregunta",
    ),
    (
        "Hola, buenos días.",
        "desconocida",
    ),
    (
        "Gracias por la atención.",
        "desconocida",
    ),
    (
        "Lo de ayer.",
        "desconocida",
    ),
    (
        "Pedido P-411.",
        "desconocida",
    ),
]


def construir_dataset():
    return [
        types.TuningExample(
            text_input=PREFIJO_ENTRADA + mensaje,
            output=json.dumps({"categoria": categoria}, ensure_ascii=False),
        )
        for mensaje, categoria in EJEMPLOS_RAW
    ]


def contar_categorias(ejemplos):
    return Counter(
        json.loads(ejemplo.output)["categoria"]
        for ejemplo in ejemplos
    )


def validar_dataset(ejemplos: list[types.TuningExample]) -> list[str]:
    problemas = []
    vistos = set()
    balance = Counter()

    if len(ejemplos) < MINIMO_EJEMPLOS:
        problemas.append(
            f"Se requieren al menos {MINIMO_EJEMPLOS} ejemplos."
        )

    for numero, ejemplo in enumerate(ejemplos, start=1):
        problemas_antes = len(problemas)
        entrada = ejemplo.text_input

        if not isinstance(entrada, str) or not entrada.strip():
            problemas.append(f"Ejemplo {numero}: entrada vacía o no textual.")
        elif not entrada.startswith(PREFIJO_ENTRADA):
            problemas.append(
                f"Ejemplo {numero}: falta la instrucción o el marcador Mensaje."
            )
        else:
            mensaje = entrada[len(PREFIJO_ENTRADA):].strip()

            if not mensaje:
                problemas.append(f"Ejemplo {numero}: mensaje vacío.")
            else:
                clave = " ".join(mensaje.split()).casefold()

                if clave in vistos:
                    problemas.append(f"Ejemplo {numero}: mensaje duplicado.")

                vistos.add(clave)

        if not isinstance(ejemplo.output, str) or not ejemplo.output.strip():
            problemas.append(f"Ejemplo {numero}: output vacío o no textual.")
            continue

        try:
            salida = json.loads(ejemplo.output)
        except json.JSONDecodeError:
            problemas.append(f"Ejemplo {numero}: output no es JSON válido.")
            continue

        if not isinstance(salida, dict) or set(salida) != {"categoria"}:
            problemas.append(
                f"Ejemplo {numero}: output debe contener únicamente categoria "
                "en un objeto JSON."
            )
            continue

        categoria = salida["categoria"]

        if not isinstance(categoria, str) or categoria not in CATEGORIAS:
            problemas.append(f"Ejemplo {numero}: categoría no permitida.")
            continue

        if len(problemas) == problemas_antes:
            balance[categoria] += 1

    faltantes = sorted(CATEGORIAS - set(balance))

    if faltantes:
        problemas.append(
            "Categorías sin ejemplos válidos: " + ", ".join(faltantes)
        )

    return problemas


if __name__ == "__main__":
    ejemplos = construir_dataset()
    problemas = validar_dataset(ejemplos)

    print(f"{len(ejemplos)} ejemplos, {len(problemas)} problemas.")

    if problemas:
        for problema in problemas:
            print("-", problema)
        raise SystemExit(1)

    balance = contar_categorias(ejemplos)

    for categoria in sorted(CATEGORIAS):
        print(f"{categoria}: {balance[categoria]}")

    print("\nDataset validado localmente, sin entrenamiento.")