import pytest

from src.recuperacion import resolver_citas


@pytest.mark.parametrize(
    "respuesta, esperado",
    [
        ("Texto [2].", {2: "memoria.py"}),
        (
            "Texto [1, 2, 3].",
            {
                1: "cliente.py",
                2: "memoria.py",
                3: "supervision.py",
            },
        ),
        ("Texto [ 1,2 ].", {1: "cliente.py", 2: "memoria.py"}),
        ("Texto [1] y [1, 2].", {1: "cliente.py", 2: "memoria.py"}),
        ("Texto [99].", {99: None}),
        ("Contexto insuficiente.", {}),
    ],
)
def test_resolver_citas_reconoce_formatos_y_fuentes(respuesta, esperado):
    citas = {
        1: "cliente.py",
        2: "memoria.py",
        3: "supervision.py",
    }

    assert resolver_citas(respuesta, citas) == esperado