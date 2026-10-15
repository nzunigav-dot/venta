from shared.herramientas import (
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    imprimir_info,
    confirmar,
)

from views import (
    ProductoController,
    VentaController,
    InventarioController,
    ClienteController,
    ProveedorController,
    CompraController,
)


class MenuCRUD:
    def __init__(self, controlador, titulo):
        self._controlador = controlador
        self._titulo = titulo
        self._activo = True

        self._opciones = {
            "1": ("Crear registro", self.crear),
            "2": ("Ver todos", self.listar),
            "3": ("Buscar", self.buscar),
            "4": ("Ver por ID", self.ver_por_id),
            "5": ("Actualizar", self.actualizar),
            "6": ("Eliminar", self.eliminar),
            "0": ("Volver", self.volver),
        }

    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(etiqueta):
        try:
            return int(input(etiqueta))
        except ValueError:
            imprimir_error("Debe ingresar un número entero.")
            return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    def pedir_datos(self):
        datos = {}

        for campo in self._controlador.MODELO.CAMPOS:
            datos[campo] = input(
                f"{campo.replace('_', ' ').capitalize()}: "
            ).strip()

        return datos

    def crear(self):
        imprimir_titulo(f"CREAR {self._controlador.NOMBRE.upper()}")
        datos = self.pedir_datos()
        self.mostrar_resultado(*self._controlador.crear(datos))
        self.pausa()

    def listar(self):
        imprimir_titulo(self._titulo.upper())
        objetos = self._controlador.listar()

        if not objetos:
            imprimir_info("No hay registros todavía.")
        else:
            for objeto in objetos:
                print(f"  {objeto}")

            imprimir_info(f"Total de registros: {len(objetos)}")

        self.pausa()

    def buscar(self):
        imprimir_titulo(f"BUSCAR {self._controlador.NOMBRE.upper()}")
        termino = input("Escriba el término que desea buscar: ")

        encontrados = self._controlador.buscar(termino)

        if not encontrados:
            imprimir_info("No se encontraron coincidencias.")
        else:
            for objeto in encontrados:
                print(f"  {objeto}")

            imprimir_info(f"Coincidencias: {len(encontrados)}")

        self.pausa()

    def ver_por_id(self):
        imprimir_titulo(f"CONSULTAR {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Ingrese el ID: ")

        objeto = (
            self._controlador.obtener(id_registro)
            if id_registro is not None
            else None
        )

        if objeto is None:
            imprimir_error("No se encontró el registro.")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {clave.replace('_', ' ').capitalize():<20}: {valor}")

        self.pausa()

    def actualizar(self):
        imprimir_titulo(f"ACTUALIZAR {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Ingrese el ID: ")

        if id_registro is None:
            self.pausa()
            return

        objeto = self._controlador.obtener(id_registro)

        if objeto is None:
            imprimir_error("No se encontró el registro.")
            self.pausa()
            return

        imprimir_info(f"Registro seleccionado: {objeto}")
        print("Deje vacío un campo si no desea cambiarlo.\n")

        cambios = {}

        for campo in self._controlador.MODELO.CAMPOS:
            actual = getattr(objeto, campo, "")
            nuevo = input(f"{campo} [{actual}]: ").strip()

            if nuevo:
                cambios[campo] = nuevo

        self.mostrar_resultado(
            *self._controlador.actualizar(id_registro, cambios)
        )
        self.pausa()

    def eliminar(self):
        imprimir_titulo(f"ELIMINAR {self._controlador.NOMBRE.upper()}")
        id_registro = self.pedir_entero("Ingrese el ID: ")

        if id_registro is None:
            self.pausa()
            return

        objeto = self._controlador.obtener(id_registro)

        if objeto is None:
            imprimir_error("No se encontró el registro.")
            self.pausa()
            return

        imprimir_info(f"Registro seleccionado: {objeto}")

        if confirmar("¿Confirma que desea eliminarlo?"):
            self.mostrar_resultado(
                *self._controlador.eliminar(id_registro)
            )
        else:
            imprimir_info("Operación cancelada.")

        self.pausa()

    def volver(self):
        self._activo = False

    def mostrar_menu(self):
        imprimir_titulo(self._titulo)

        for tecla, (texto, _) in self._opciones.items():
            print(f"  {tecla}. {texto}")

        print()

    def ejecutar(self):
        self._activo = True

        while self._activo:
            self.mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()

            if opcion not in self._opciones:
                imprimir_error("Opción no válida.")
                self.pausa()
                continue

            try:
                self._opciones[opcion][1]()
            except (ValueError, TypeError, OSError) as error:
                imprimir_error(f"No se pudo completar la operación: {error}")
                self.pausa()


def main():
    modulos = {
        "1": ("PRODUCTOS", ProductoController, "LISTA DE PRODUCTOS"),
        "2": ("VENTAS", VentaController, "REGISTRO DE VENTAS"),
        "3": ("INVENTARIO", InventarioController, "MOVIMIENTOS DE INVENTARIO"),
        "4": ("CLIENTES", ClienteController, "LISTA DE CLIENTES"),
        "5": ("PROVEEDORES", ProveedorController, "LISTA DE PROVEEDORES"),
        "6": ("COMPRAS", CompraController, "REGISTRO DE COMPRAS"),
    }

    while True:
        imprimir_titulo("SISTEMA DE VENTA")
        print("  1. Productos")
        print("  2. Ventas")
        print("  3. Inventario")
        print("  4. Clientes")
        print("  5. Proveedores")
        print("  6. Compras")
        print("  0. Salir")
        print()

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            imprimir_info("Gracias por utilizar el sistema de venta.")
            break

        if opcion not in modulos:
            imprimir_error("Opción no válida.")
            input("Presione Enter para continuar...")
            continue

        titulo, controlador_clase, encabezado = modulos[opcion]
        controlador = controlador_clase()
        menu = MenuCRUD(controlador, encabezado)
        menu.ejecutar()


if __name__ == "__main__":
    main()
