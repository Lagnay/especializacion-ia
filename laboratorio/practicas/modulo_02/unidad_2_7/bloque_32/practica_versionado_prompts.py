import hashlib
import difflib
from datetime import datetime, timezone


def comparar_prompts(anterior, nueva):
    return list(
        difflib.unified_diff(
            anterior.split(),
            nueva.split(),
            fromfile="version_anterior",
            tofile="version_nueva",
            lineterm="",
        )
    )


class RegistroDePrompts:
    def __init__(self):
        self.versiones = []

    def registrar(self, nombre, texto, autor, nota):
        version = {
            "nombre": nombre,
            "huella": hashlib.sha256(
                texto.encode("utf-8")
            ).hexdigest(),
            "texto": texto,
            "autor": autor,
            "fecha": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "nota": nota,
        }

        self.versiones.append(version)
        return version

    def ultima(self, nombre):
        candidatas = [
            version
            for version in self.versiones
            if version["nombre"] == nombre
        ]

        return candidatas[-1] if candidatas else None


if __name__ == "__main__":
    registro = RegistroDePrompts()

    texto_inicial = "Responde usando solo el contexto proporcionado."
    texto_nuevo = (
        texto_inicial
        + " Si falta información, indícalo."
    )

    registro.registrar(
        "prompt_ejemplo",
        texto_inicial,
        "laboratorio",
        "Versión didáctica inicial.",
    )
    registro.registrar(
        "prompt_ejemplo",
        texto_nuevo,
        "laboratorio",
        "Indica qué hacer si falta información.",
    )

    for version in registro.versiones:
        print(
            version["huella"][:12],
            "-",
            version["nota"],
        )

    primera, segunda = registro.versiones

    print("Huellas distintas:", primera["huella"] != segunda["huella"])
    print(
        "Última registrada:",
        registro.ultima("prompt_ejemplo")["huella"][:12],
    )
    print("Prompt inexistente:", registro.ultima("otro_prompt"))
    print("\n=== DIFERENCIAS ===")

    for linea in comparar_prompts(
        primera["texto"],
        segunda["texto"],
    ):
        print(linea)