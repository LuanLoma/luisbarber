class Registro:
    """Modelo básico para representar un registro del negocio.

    Este modelo es genérico. Los alumnos pueden adaptarlo a:
    producto, servicio, cita, reparación, pedido, etc.
    """

    def __init__(self, id, nombre, categoria, descripcion, precio=0, activo=True):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.descripcion = descripcion
        self.precio = precio
        self.activo = activo

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "activo": self.activo
        }
