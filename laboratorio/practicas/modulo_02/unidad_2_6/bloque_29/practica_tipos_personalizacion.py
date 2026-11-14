from importlib.metadata import version

from google.genai import types


if __name__ == "__main__":
    print("google-genai:", version("google-genai"))

    print("\nModos definidos en el SDK:")
    for modo in types.TuningMode:
        print("-", modo.value)

    print("\nTamaños de adapter definidos en el SDK:")
    for tamano in types.AdapterSize:
        print("-", tamano.value)

    print("\nComprobación local terminada.")
    print("No se creó ningún cliente ni se envió un trabajo.")