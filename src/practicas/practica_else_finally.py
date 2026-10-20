def dividir(a, b):
    try:
        resultado = a / b
    except ZeroDivisionError:
        print("No se puede dividir entre cero.")
    else:
        print("Resultado:", resultado)
    finally:
        print("Finalizó este intento de división.")


print("=== CASO CORRECTO ===")
dividir(10, 2)

print("\n=== DIVISIÓN POR CERO ===")
dividir(10, 0)