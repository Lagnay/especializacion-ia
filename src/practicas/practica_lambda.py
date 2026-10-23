from src.practicas.practica_reintento_reutilizable import (
    con_reintento,
)


def sumar(a, b):
    return a + b


def operacion_con_nombre():
    return sumar(2, 3)


if __name__ == "__main__":
    resultado_con_nombre = con_reintento(
        operacion_con_nombre
    )

    resultado_con_lambda = con_reintento(
        lambda: sumar(2, 3)
    )

    print("Con función nombrada:", resultado_con_nombre)
    print("Con lambda:", resultado_con_lambda)