import time
import random
from typing import Any, Callable


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    if intentos < 1:
        raise ValueError("Debe permitirse al menos un intento.")

    for intento in range(1, intentos + 1):
        try:
            return funcion()

        except TimeoutError:
            if intento == intentos:
                raise

            espera_calculada = min(
                espera_base * (2 ** (intento - 1)),
                espera_maxima,
            )

            jitter = random.uniform(0, espera_calculada * 0.1)

            espera = min(
                espera_calculada + jitter,
                espera_maxima,
            )

            print(
                f"Intento {intento} de {intentos} fallido. "
                f"Esperando {espera:.2f} segundos..."
            )
            time.sleep(espera)


intentos_previos = 0


def operacion_simulada():
    global intentos_previos
    intentos_previos += 1

    print(f"Ejecutando intento {intentos_previos}")

    if intentos_previos < 4:
        raise TimeoutError("Fallo temporal simulado.")

    return "Respuesta simulada recibida correctamente."


if __name__ == "__main__":
    try:
        resultado = con_reintento(
            operacion_simulada,
            intentos=4,
            espera_base=2,
            espera_maxima=10,
        )
        print("Resultado:", resultado)

    except (ValueError, TimeoutError) as error:
        print("No se pudo completar la operación:", error)

    print("El programa llegó al final.")