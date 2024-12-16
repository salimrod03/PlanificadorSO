class Recurso:
    def __init__(self, nombre, cantidad):
        self.nombre = nombre
        self.cantidad = cantidad
        self.asignados = 0

    def puede_asignar(self, cantidad_solicitada):
        return (self.cantidad - self.asignados) >= cantidad_solicitada

    def asignar(self, cantidad):
        if self.puede_asignar(cantidad):
            self.asignados += cantidad
            return True
        return False

    def liberar(self, cantidad):
        self.asignados -= cantidad
