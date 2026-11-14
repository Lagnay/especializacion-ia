from contextvars import ContextVar
from uuid import uuid4


trace_id_var = ContextVar("trace_id", default=None)


def sub_paso():
    print("Dentro del subpaso:", trace_id_var.get())


def procesar(pregunta):
    token = trace_id_var.set("trace-" + uuid4().hex)

    try:
        print("Caracteres de la pregunta:", len(pregunta))
        print("Dentro de procesar:", trace_id_var.get())
        sub_paso()
    finally:
        trace_id_var.reset(token)


if __name__ == "__main__":
    pregunta = "¿Dónde consulto mi pedido?"

    for numero in (1, 2):
        print(f"\n=== CONSULTA {numero} ===")
        procesar(pregunta)
        print("Fuera de la consulta:", trace_id_var.get())