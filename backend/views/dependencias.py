"""
Dependencias de FastAPI para saber quién hace el pedido. Las usan todas las vistas protegidas.
"""

from typing import Optional

from fastapi import Cookie, Depends

from backend.controller import autenticacion
from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import Usuario

COOKIE_SESION = "sesion"


def token_de_sesion(sesion: Optional[str] = Cookie(default=None)) -> Optional[str]:
    return sesion


def usuario_con_sesion(token: Optional[str] = Depends(token_de_sesion)) -> Usuario:
    """Cualquier sesión válida, aunque tenga que cambiar la contraseña: solo para /auth/yo y elegirla."""
    return autenticacion.usuario_de_sesion(token)


def usuario_actual(usuario: Usuario = Depends(usuario_con_sesion)) -> Usuario:
    autenticacion.exigir_contrasena_definitiva(usuario)
    return usuario


def requiere_admin(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    if not usuario.es_admin:
        raise ErrorDeNegocio("sin_permiso", "No tenés permiso para hacer esto.")
    return usuario
