from pathlib import Path

from models import (
    Producto, Venta, Inventario,
    Cliente, Proveedor, Compra
)
from shared.json_manager import GestorJSON


DATA_DIR = Path(__file__).resolve().parent / "data"


class CrudBase:
    MODELO = None
    ARCHIVO = None
    NOMBRE = "registro"
    CAMPOS_BUSCABLES = ()

    def __init__(self):
        self._gestor = GestorJSON(DATA_DIR / self.ARCHIVO)

    def registros(self):
        return self._gestor.leer()

    def listar(self):
        return [
            self.MODELO.desde_diccionario(r)
            for r in self.registros()
        ]

    def obtener(self, id_registro):
        for objeto in self.listar():
            if objeto.id == id_registro:
                return objeto
        return None

    def siguiente_id(self):
        ids = [r.get("id", 0) for r in self.registros()]
        return max(ids, default=0) + 1

    def buscar(self, termino):
        termino = str(termino).strip().lower()

        if not termino:
            return []

        resultados = []

        for registro in self.registros():
            for campo in self.CAMPOS_BUSCABLES:
                valor = str(registro.get(campo, "")).lower()

                if termino in valor:
                    resultados.append(
                        self.MODELO.desde_diccionario(registro)
                    )
                    break

        return resultados

    def validar(self, datos, id_actual=None):
        for campo in self.MODELO.OBLIGATORIOS:
            valor = datos.get(campo, "")

            if str(valor).strip() == "":
                return f"El campo '{campo}' es obligatorio."

        try:
            for campo in self.MODELO.NUMERICOS:
                valor = float(datos[campo])
                if valor < 0:
                    return f"'{campo}' no puede ser negativo."

            for campo in self.MODELO.ENTEROS:
                valor = int(datos[campo])
                if valor < 0:
                    return f"'{campo}' no puede ser negativo."

        except (ValueError, TypeError):
            return "Revise los campos numéricos."

        if "cantidad" in datos and int(datos["cantidad"]) <= 0:
            return "La cantidad debe ser mayor que cero."

        if "email" in datos:
            email = str(datos["email"]).strip()

            if "@" not in email or "." not in email.split("@")[-1]:
                return "El correo electrónico no es válido."

        return None

    def preparar(self, datos):
        resultado = {}

        for campo in self.MODELO.CAMPOS:
            valor = datos.get(campo, "")
            resultado[campo] = self.MODELO.convertir(campo, valor)

        return resultado

    def crear(self, datos):
        error = self.validar(datos)

        if error:
            return False, error

        try:
            objeto = self.MODELO(
                self.siguiente_id(),
                **self.preparar(datos)
            )
        except (ValueError, TypeError) as error:
            return False, f"Datos inválidos: {error}"

        registros = self.registros()
        registros.append(objeto.a_diccionario())

        if not self._gestor.guardar(registros):
            return False, "No se pudo guardar el registro."

        return True, f"{self.NOMBRE.capitalize()} creado: {objeto.etiqueta()}"

    def actualizar(self, id_registro, cambios):
        objeto = self.obtener(id_registro)

        if objeto is None:
            return False, "No se encontró el registro."

        campos_invalidos = set(cambios) - set(self.MODELO.CAMPOS)

        if campos_invalidos:
            return False, "Se indicaron campos no válidos."

        if not cambios:
            return False, "No indicó cambios."

        datos_completos = objeto.a_diccionario()

        for campo, valor in cambios.items():
            datos_completos[campo] = valor

        error = self.validar(datos_completos, id_actual=id_registro)

        if error:
            return False, error

        try:
            nuevos_datos = self.preparar(datos_completos)

            objeto = self.MODELO(
                id_registro,
                **nuevos_datos
            )
        except (ValueError, TypeError) as error:
            return False, f"Datos inválidos: {error}"

        registros = self.registros()

        for indice, registro in enumerate(registros):
            if registro.get("id") == id_registro:
                registros[indice] = objeto.a_diccionario()
                break

        if not self._gestor.guardar(registros):
            return False, "No se pudo actualizar el registro."

        return True, "Registro actualizado correctamente."

    def eliminar(self, id_registro):
        registros = self.registros()
        restantes = [
            r for r in registros
            if r.get("id") != id_registro
        ]

        if len(restantes) == len(registros):
            return False, "No se encontró el registro."

        if not self._gestor.guardar(restantes):
            return False, "No se pudo eliminar el registro."

        return True, "Registro eliminado correctamente."

    def ajustar_stock(self, producto_id, variacion):
        gestor_productos = GestorJSON(DATA_DIR / "productos.json")
        productos = gestor_productos.leer()

        for producto in productos:
            if producto.get("id") == int(producto_id):
                nuevo_stock = int(producto.get("stock", 0)) + int(variacion)

                if nuevo_stock < 0:
                    return False

                producto["stock"] = nuevo_stock
                return gestor_productos.guardar(productos)

        return False

    def producto_existe(self, producto_id):
        gestor = GestorJSON(DATA_DIR / "productos.json")

        return any(
            p.get("id") == int(producto_id)
            for p in gestor.leer()
        )

    def cliente_existe(self, cliente_id):
        gestor = GestorJSON(DATA_DIR / "clientes.json")

        return any(
            c.get("id") == int(cliente_id)
            for c in gestor.leer()
        )

    def proveedor_existe(self, proveedor_id):
        gestor = GestorJSON(DATA_DIR / "proveedores.json")

        return any(
            p.get("id") == int(proveedor_id)
            for p in gestor.leer()
        )


class ProductoController(CrudBase):
    MODELO = Producto
    ARCHIVO = "productos.json"
    NOMBRE = "producto"
    CAMPOS_BUSCABLES = ("nombre", "descripcion")

    def validar(self, datos, id_actual=None):
        error = super().validar(datos, id_actual)

        if error:
            return error

        if float(datos["precio"]) <= 0:
            return "El precio debe ser mayor que cero."

        return None


class ClienteController(CrudBase):
    MODELO = Cliente
    ARCHIVO = "clientes.json"
    NOMBRE = "cliente"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "telefono", "email")


class ProveedorController(CrudBase):
    MODELO = Proveedor
    ARCHIVO = "proveedores.json"
    NOMBRE = "proveedor"
    CAMPOS_BUSCABLES = ("nombre", "telefono", "email", "direccion")


class VentaController(CrudBase):
    MODELO = Venta
    ARCHIVO = "ventas.json"
    NOMBRE = "venta"
    CAMPOS_BUSCABLES = ("cliente_id", "producto_id", "fecha")

    def validar(self, datos, id_actual=None):
        error = super().validar(datos, id_actual)

        if error:
            return error

        if int(datos["cantidad"]) <= 0:
            return "La cantidad debe ser mayor que cero."

        if not self.cliente_existe(datos["cliente_id"]):
            return "El cliente indicado no existe."

        if not self.producto_existe(datos["producto_id"]):
            return "El producto indicado no existe."

        gestor = GestorJSON(DATA_DIR / "productos.json")
        producto = next(
            (
                p for p in gestor.leer()
                if p["id"] == int(datos["producto_id"])
            ),
            None
        )

        if producto is None:
            return "No se encontró el producto."

        if int(producto["stock"]) < int(datos["cantidad"]):
            return f"Stock insuficiente. Disponible: {producto['stock']}."

        return None

    def crear(self, datos):
        error = self.validar(datos)

        if error:
            return False, error

        exito, mensaje = super().crear(datos)

        if not exito:
            return False, mensaje

        if not self.ajustar_stock(
            datos["producto_id"], -int(datos["cantidad"])
        ):
            # Retirar la venta si no se pudo ajustar el stock.
            registros = self.registros()
            if registros:
                registros.pop()
                self._gestor.guardar(registros)

            return False, "No se pudo actualizar el inventario."

        return True, mensaje

    def actualizar(self, id_registro, cambios):
        return False, (
            "Para conservar el stock correcto, elimine la venta "
            "y registre una nueva."
        )

    def eliminar(self, id_registro):
        venta = self.obtener(id_registro)

        if venta is None:
            return False, "No se encontró la venta."

        if not self.ajustar_stock(venta.producto_id, venta.cantidad):
            return False, "No se pudo devolver el producto al inventario."

        exito, mensaje = super().eliminar(id_registro)

        if not exito:
            self.ajustar_stock(venta.producto_id, -venta.cantidad)

        return exito, mensaje


class CompraController(CrudBase):
    MODELO = Compra
    ARCHIVO = "compras.json"
    NOMBRE = "compra"
    CAMPOS_BUSCABLES = ("proveedor_id", "producto_id", "fecha")

    def validar(self, datos, id_actual=None):
        error = super().validar(datos, id_actual)

        if error:
            return error

        if int(datos["cantidad"]) <= 0:
            return "La cantidad debe ser mayor que cero."

        if float(datos["costo_unitario"]) <= 0:
            return "El costo debe ser mayor que cero."

        if not self.proveedor_existe(datos["proveedor_id"]):
            return "El proveedor indicado no existe."

        if not self.producto_existe(datos["producto_id"]):
            return "El producto indicado no existe."

        return None

    def crear(self, datos):
        error = self.validar(datos)

        if error:
            return False, error

        exito, mensaje = super().crear(datos)

        if not exito:
            return False, mensaje

        if not self.ajustar_stock(
            datos["producto_id"], int(datos["cantidad"])
        ):
            registros = self.registros()
            if registros:
                registros.pop()
                self._gestor.guardar(registros)

            return False, "No se pudo actualizar el inventario."

        return True, mensaje

    def actualizar(self, id_registro, cambios):
        return False, (
            "Para conservar el stock correcto, elimine la compra "
            "y registre una nueva."
        )

    def eliminar(self, id_registro):
        compra = self.obtener(id_registro)

        if compra is None:
            return False, "No se encontró la compra."

        if not self.ajustar_stock(
            compra.producto_id, -compra.cantidad
        ):
            return False, (
                "No se puede eliminar: las unidades compradas "
                "ya no están disponibles en el inventario."
            )

        exito, mensaje = super().eliminar(id_registro)

        if not exito:
            self.ajustar_stock(compra.producto_id, compra.cantidad)

        return exito, mensaje


class InventarioController(CrudBase):
    MODELO = Inventario
    ARCHIVO = "inventario.json"
    NOMBRE = "movimiento de inventario"
    CAMPOS_BUSCABLES = ("producto_id", "tipo_movimiento", "fecha", "detalle")

    def validar(self, datos, id_actual=None):
        error = super().validar(datos, id_actual)

        if error:
            return error

        if not self.producto_existe(datos["producto_id"]):
            return "El producto indicado no existe."

        tipo = str(datos["tipo_movimiento"]).strip().lower()

        if tipo not in ("entrada", "salida"):
            return "El movimiento debe ser 'entrada' o 'salida'."

        return None

    def crear(self, datos):
        error = self.validar(datos)

        if error:
            return False, error

        cantidad = int(datos["cantidad"])
        tipo = str(datos["tipo_movimiento"]).strip().lower()

        variacion = cantidad if tipo == "entrada" else -cantidad

        # Comprobar stock antes de registrar una salida.
        if not self.producto_existe(datos["producto_id"]):
            return False, "El producto no existe."

        if variacion < 0:
            gestor = GestorJSON(DATA_DIR / "productos.json")
            producto = next(
                (
                    p for p in gestor.leer()
                    if p["id"] == int(datos["producto_id"])
                ),
                None
            )

            if producto is None or producto["stock"] < cantidad:
                return False, "No hay suficiente stock para esa salida."

        exito, mensaje = super().crear(datos)

        if not exito:
            return False, mensaje

        if not self.ajustar_stock(datos["producto_id"], variacion):
            registros = self.registros()
            if registros:
                registros.pop()
                self._gestor.guardar(registros)

            return False, "No se pudo actualizar el stock."

        return True, mensaje

    def actualizar(self, id_registro, cambios):
        return False, (
            "Para conservar el stock correcto, elimine el movimiento "
            "y registre uno nuevo."
        )

    def eliminar(self, id_registro):
        movimiento = self.obtener(id_registro)

        if movimiento is None:
            return False, "No se encontró el movimiento."

        tipo = movimiento.tipo_movimiento.lower()
        variacion = (
            -movimiento.cantidad
            if tipo == "entrada"
            else movimiento.cantidad
        )

        if not self.ajustar_stock(movimiento.producto_id, variacion):
            return False, (
                "No se puede eliminar el movimiento porque "
                "el stock resultante sería negativo."
            )

        exito, mensaje = super().eliminar(id_registro)

        if not exito:
            self.ajustar_stock(movimiento.producto_id, -variacion)

        return exito, mensaje
