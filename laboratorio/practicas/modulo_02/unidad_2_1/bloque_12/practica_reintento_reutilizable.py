import time
from typing import Callable, Any


intentos_realizados = 0


def operacion_simulada():
    global intentos_realizados

    intentos_realizados += 1
    print(f"Ejecutando intento {intentos_realizados}")

    if intentos_realizados <= 2:
        raise TimeoutError("Fallo temporal simulado.")

    return "Respuesta simulada recibida correctamente."


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:
    if intentos < 1:
        raise ValueError("Debe permitirse al menos un intento.")

    for intento in range(1, intentos + 1):
        try:
            return funcion()

        except TimeoutError:
            if intento == intentos:
                raise

            print(
                f"Intento {intento} de {intentos} fallido. "
                f"Esperando {espera_segundos} segundos..."
            )
            time.sleep(espera_segundos)


if __name__ == "__main__":
    try:
        resultado = con_reintento(operacion_simulada)
        print("Resultado:", resultado)

    except (TimeoutError, ValueError) as error:
        print("No se pudo completar la operación:", error)

    print("El programa llegó al final.")