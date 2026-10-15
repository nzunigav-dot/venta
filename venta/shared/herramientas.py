import os

COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AMARILLO": "\033[93m",
    "AZUL": "\033[94m",
    "MORADO": "\033[95m",
    "CYAN": "\033[96m",
    "BLANCO": "\033[97m",
    "RESET": "\033[0m",
    "NEGRITA": "\033[1m",
}


def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def imprimir_color(mensaje, color="BLANCO"):
    codigo = COLORES.get(color.upper(), COLORES["BLANCO"])
    print(f"{codigo}{mensaje}{COLORES['RESET']}")


def imprimir_titulo(titulo):
    print()
    imprimir_color("=" * 55, "CYAN")
    imprimir_color(titulo.center(55), "AMARILLO")
    imprimir_color("=" * 55, "CYAN")
    print()


def imprimir_exito(mensaje):
    imprimir_color(f"[ÉXITO] {mensaje}", "VERDE")


def imprimir_error(mensaje):
    imprimir_color(f"[ERROR] {mensaje}", "ROJO")


def imprimir_info(mensaje):
    imprimir_color(f"[INFO] {mensaje}", "AZUL")


def confirmar(mensaje="¿Está seguro?"):
    respuesta = input(f"{mensaje} (s/n): ").strip().lower()
    return respuesta in ("s", "si", "sí", "y", "yes")


def pausa():
    input("\nPresione Enter para continuar...")