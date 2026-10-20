"""
Errores de negocio. Llevan un código estable (para que el frontend decida qué mostrar)
y un mensaje en español; la capa de presentación los traduce a códigos HTTP.
"""


class ErrorDeNegocio(Exception):
    def __init__(self, codigo: str, mensaje: str):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
