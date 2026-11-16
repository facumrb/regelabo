"""
Usuarios en el panel de admin (decisión 028, etapa 3): lista con totales, desbloquear,
contraseña temporal y verificar el email a mano. Nada de esto se aplica a otros admin:
esas cuentas se manejan solo por comando.
"""

import secrets
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from backend.controller import autenticacion
from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import (ContrasenaTemporal, PaginaDeUsuarios, Pendientes, TipoPerfil,
                                        UsuarioAdmin)
from backend.datos import comentarios, usuarios
from backend.datos.conexion import transaccion


def listar(limite: int, despues_de: Optional[UUID], busqueda: Optional[str],
           tipo: Optional[TipoPerfil], con_pedido: bool = False) -> PaginaDeUsuarios:
    busqueda = (busqueda or "").strip() or None
    with transaccion() as tx:
        # uno de más: dice si hay página siguiente
        pagina = usuarios.listar_para_admin(tx, limite + 1, despues_de, busqueda, tipo, con_pedido)
    hay_mas = len(pagina) > limite
    pagina = pagina[:limite]
    return PaginaDeUsuarios(usuarios=pagina, siguiente=pagina[-1].id if hay_mas else None)


def _comun(tx, usuario_id: UUID):
    usuario = usuarios.buscar(tx, usuario_id)
    if usuario is None:
        raise ErrorDeNegocio("usuario_no_encontrado", "El usuario no existe.")
    if usuario.es_admin:
        raise ErrorDeNegocio("usuario_es_admin", "Las cuentas de admin solo se manejan por comando.")
    return usuario


def desbloquear(usuario_id: UUID) -> UsuarioAdmin:
    with transaccion() as tx:
        _comun(tx, usuario_id)
        usuarios.reiniciar_intentos(tx, usuario_id)
        return usuarios.ver_para_admin(tx, usuario_id)


def verificar_email(usuario_id: UUID) -> UsuarioAdmin:
    """RN15 a mano: para cuando el mail no llega. Si ya estaba verificado, no cambia nada."""
    with transaccion() as tx:
        _comun(tx, usuario_id)
        usuarios.marcar_verificado(tx, usuario_id, datetime.now(timezone.utc))
        return usuarios.ver_para_admin(tx, usuario_id)


def resetear_contrasena(usuario_id: UUID) -> ContrasenaTemporal:
    """Solo si el usuario lo pidió en "olvidé mi contraseña". Contraseña al azar que el admin le manda
    por mail; también desbloquea, cierra las sesiones y da el pedido por atendido."""
    with transaccion() as tx:
        usuario = _comun(tx, usuario_id)
    if usuario.restablecimiento_pedido_en is None:
        raise ErrorDeNegocio("sin_pedido_de_restablecimiento",
                             "El usuario no pidió restablecer la contraseña.")
    email = usuario.email
    temporal = secrets.token_urlsafe(12)  # 16 caracteres
    autenticacion.resetear_contrasena(email, temporal)
    return ContrasenaTemporal(contrasena_temporal=temporal)


def pendientes() -> Pendientes:
    """Lo que el admin tiene para revisar: alimenta el contador del menú."""
    with transaccion() as tx:
        return Pendientes(comentarios_nuevos=comentarios.contar_nuevos(tx),
                          restablecimientos=usuarios.contar_pedidos_de_restablecimiento(tx))
