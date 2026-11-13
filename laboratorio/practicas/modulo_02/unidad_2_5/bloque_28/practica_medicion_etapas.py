import time
from contextlib import contextmanager


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()

    try:
        yield
    finally:
        tiempos[etapa] = time.perf_counter() - inicio


if __name__ == "__main__":
    tiempos = {}
    inicio_total = time.perf_counter()

    with medir(tiempos, "embedding_simulado"):
        time.sleep(0.05)

    with medir(tiempos, "busqueda_simulada"):
        time.sleep(0.01)

    with medir(tiempos, "generacion_simulada"):
        time.sleep(0.10)

    total = time.perf_counter() - inicio_total

    for etapa, segundos in tiempos.items():
        print(f"{etapa}: {segundos * 1000:.2f} ms")

    print(
        f"Suma de etapas: "
        f"{sum(tiempos.values()) * 1000:.2f} ms"
    )
    print(
        f"Tiempo total transcurrido: "
        f"{total * 1000:.2f} ms"
    )