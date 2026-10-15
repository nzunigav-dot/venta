from abc import ABC, abstractmethod


class ModeloBase(ABC):
    CAMPOS = ()
    OBLIGATORIOS = ()
    NUMERICOS = ()
    ENTEROS = ()

    def __init__(self, id_registro, **datos):
        self.id = int(id_registro)

        for campo in self.CAMPOS:
            valor = datos.get(campo, "")
            setattr(self, campo, self.convertir(campo, valor))

    @classmethod
    def convertir(cls, campo, valor):
        if campo in cls.ENTEROS:
            if str(valor).strip() == "":
                return 0
            return int(valor)

        if campo in cls.NUMERICOS:
            if str(valor).strip() == "":
                return 0.0
            return float(valor)

        return str(valor).strip()

    @classmethod
    def desde_diccionario(cls, datos):
        valores = {
            campo: datos.get(campo, "")
            for campo in cls.CAMPOS
        }
        return cls(datos["id"], **valores)

    def a_diccionario(self):
        datos = {"id": self.id}

        for campo in self.CAMPOS:
            datos[campo] = getattr(self, campo)

        return datos

    @abstractmethod
    def etiqueta(self):
        pass

    def __str__(self):
        return f"[{self.id}] {self.etiqueta()}"


class Producto(ModeloBase):
    CAMPOS = (
        "nombre", "descripcion", "precio", "stock", "stock_minimo"
    )
    OBLIGATORIOS = ("nombre", "precio", "stock", "stock_minimo")
    NUMERICOS = ("precio",)
    ENTEROS = ("stock", "stock_minimo")

    def etiqueta(self):
        return (
            f"{self.nombre} | Precio: ${self.precio:.2f} "
            f"| Stock: {self.stock}"
        )


class Cliente(ModeloBase):
    CAMPOS = ("nombre", "apellido", "telefono", "email")
    OBLIGATORIOS = ("nombre", "apellido", "telefono", "email")

    def etiqueta(self):
        return f"{self.nombre} {self.apellido} | {self.telefono}"


class Proveedor(ModeloBase):
    CAMPOS = ("nombre", "telefono", "email", "direccion")
    OBLIGATORIOS = ("nombre", "telefono", "email", "direccion")

    def etiqueta(self):
        return f"{self.nombre} | Teléfono: {self.telefono}"


class Venta(ModeloBase):
    CAMPOS = (
        "cliente_id", "producto_id", "cantidad",
        "precio_unitario", "fecha"
    )
    OBLIGATORIOS = CAMPOS
    NUMERICOS = ("precio_unitario",)
    ENTEROS = ("cliente_id", "producto_id", "cantidad")

    def etiqueta(self):
        return (
            f"Cliente ID: {self.cliente_id} | "
            f"Producto ID: {self.producto_id} | "
            f"Cantidad: {self.cantidad} | "
            f"Total: ${self.cantidad * self.precio_unitario:.2f}"
        )


class Compra(ModeloBase):
    CAMPOS = (
        "proveedor_id", "producto_id", "cantidad",
        "costo_unitario", "fecha"
    )
    OBLIGATORIOS = CAMPOS
    NUMERICOS = ("costo_unitario",)
    ENTEROS = ("proveedor_id", "producto_id", "cantidad")

    def etiqueta(self):
        return (
            f"Proveedor ID: {self.proveedor_id} | "
            f"Producto ID: {self.producto_id} | "
            f"Cantidad: {self.cantidad} | "
            f"Total: ${self.cantidad * self.costo_unitario:.2f}"
        )


class Inventario(ModeloBase):
    CAMPOS = (
        "producto_id", "tipo_movimiento",
        "cantidad", "fecha", "detalle"
    )
    OBLIGATORIOS = (
        "producto_id", "tipo_movimiento", "cantidad", "fecha"
    )
    ENTEROS = ("producto_id", "cantidad")

    def etiqueta(self):
        return (
            f"Producto ID: {self.producto_id} | "
            f"{self.tipo_movimiento} | Cantidad: {self.cantidad}"
        )
