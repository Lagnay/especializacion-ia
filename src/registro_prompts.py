import difflib
import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


def huella_prompt(texto):
    if not isinstance(texto, str):
        raise TypeError("El prompt debe ser texto.")
    if not texto.strip():
        raise ValueError("El prompt no puede estar vacío.")

    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def comparar_prompts(anterior, nueva):
    huella_prompt(anterior)
    huella_prompt(nueva)

    return list(difflib.unified_diff(
        anterior.split(),
        nueva.split(),
        fromfile="version_anterior",
        tofile="version_nueva",
        lineterm="",
    ))


class RegistroDePrompts:
    def __init__(self):
        self._versiones = []

    @property
    def versiones(self):
        return deepcopy(self._versiones)

    def registrar(self, nombre, texto, autor, nota, *, validacion):
        for campo, valor in (
            ("nombre", nombre),
            ("autor", autor),
            ("nota", nota),
        ):
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(
                    f"{campo} debe ser texto con contenido."
                )

        if not isinstance(validacion, dict):
            raise TypeError(
                "La validación debe ser un diccionario."
            )

        version = {
            "nombre": nombre,
            "huella": huella_prompt(texto),
            "texto": texto,
            "autor": autor,
            "fecha": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "nota": nota,
            "validacion": deepcopy(validacion),
        }

        self._versiones.append(version)
        return deepcopy(version)

    def ultima(self, nombre):
        for version in reversed(self._versiones):
            if version["nombre"] == nombre:
                return deepcopy(version)

        return None


def construir_registro_laboratorio():
    from src.seguridad_rag import INSTRUCCION_SISTEMA

    raiz = Path(__file__).resolve().parents[1]
    evidencia = (
        raiz
        / "docs/modulo_02/unidad_2_5/bloque_28"
        / "registros_latencia_costo.jsonl"
    )

    registros = [
        json.loads(linea)
        for linea in evidencia.read_text(
            encoding="utf-8-sig"
        ).splitlines()
        if linea.strip()
    ]

    historico = registros[0]
    texto_anterior, separador, _ = historico["prompt"].partition(
        "\n\nContexto:\n"
    )

    if not separador:
        raise ValueError(
            "La evidencia no tiene el formato esperado."
        )

    registro = RegistroDePrompts()

    registro.registrar(
        "instrucciones_rag",
        texto_anterior,
        "laboratorio",
        "Instrucciones incluidas en el prompt del Bloque 28.",
        validacion={
            "tipo": "consulta_real",
            "referencia": evidencia.relative_to(raiz).as_posix(),
            "fecha_evidencia": historico["timestamp"],
            "configuracion": historico["configuracion"],
        },
    )

    registro.registrar(
        "instrucciones_rag",
        INSTRUCCION_SISTEMA,
        "laboratorio",
        "Instrucciones de sistema con mitigación del Bloque 31.",
        validacion={
            "tipo": "simulada",
            "referencia": (
                "docs/modulo_02/unidad_2_7/bloque_31/"
                "trazas_rag_simuladas.jsonl"
            ),
            "modelo_real": None,
            "parametros_modelo_real": None,
        },
    )

    return registro


if __name__ == "__main__":
    registro = construir_registro_laboratorio()
    anterior, nueva = registro.versiones

    for version in registro.versiones:
        print(
            version["huella"][:12],
            "| validación:", version["validacion"]["tipo"],
        )

    print(
        "Huellas distintas:",
        anterior["huella"] != nueva["huella"],
    )
    print(
        "Última registrada:",
        registro.ultima("instrucciones_rag")["huella"][:12],
    )
    print("Registrar no activa una versión.")

    print("\n=== DIFERENCIAS ===")
    for linea in comparar_prompts(
        anterior["texto"], nueva["texto"]
    ):
        print(linea)