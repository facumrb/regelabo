"""
Registro, inicio y cierre de sesión.

La sesión es un token aleatorio que viaja en una cookie; en la base solo se guarda su hash,
así que leer la tabla `sesion` no alcanza para usar una sesión.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import cache
from typing import Optional, Tuple

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from backend.configuracion import BLOQUEO_MINUTOS, INTENTOS_MAX, SESION_HORAS
from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import RegistroInput, Usuario
from backend.datos import sesiones, usuarios
from backend.datos.conexion import transaccion

_hasher = PasswordHasher()  # argon2id

_CREDENCIALES_INVALIDAS = ErrorDeNegocio("credenciales_invalidas", "Email o contraseña incorrectos.")
_NO_AUTENTICADO = ErrorDeNegocio("no_autenticado", "Tenés que iniciar sesión.")


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _verificar(hash_guardado: str, contrasena: str) -> bool:
    try:
        return _hasher.verify(hash_guardado, contrasena)
    except (VerificationError, InvalidHashError):
        return False


@cache
def _hash_de_relleno() -> str:
    return _hasher.hash("relleno")


def validar_contrasena(contrasena: str) -> None:
    # El máximo evita que alguien nos haga hashear textos enormes
    if not 8 <= len(contrasena) <= 128:
        raise ErrorDeNegocio("contrasena_invalida", "La contraseña debe tener entre 8 y 128 caracteres.")


def registrar(datos: RegistroInput) -> Usuario:
    if not datos.acepta_aviso:
        raise ErrorDeNegocio("aviso_no_aceptado", "Tenés que aceptar el aviso de uso no profesional.")
    validar_contrasena(datos.password)
    with transaccion() as tx:
        usuario = usuarios.crear(tx, datos.email.lower(), _hasher.hash(datos.password), datos.nombre,
                                 datos.tipo_perfil, es_admin=False, aviso_aceptado_en=_ahora())
    if usuario is None:
        raise ErrorDeNegocio("email_ya_registrado", "Ya existe una cuenta con ese email.")
    return usuario


def iniciar_sesion(email: str, contrasena: str) -> Tuple[str, Usuario]:
    """Devuelve el token para la cookie y el usuario. Los errores se lanzan DESPUÉS de cerrar la
    transacción, para que el intento fallido quede registrado en lugar de revertirse."""
    ahora = _ahora()
    error: Optional[ErrorDeNegocio] = None
    token = ""
    with transaccion() as tx:
        usuario = usuarios.buscar_por_email(tx, email.strip().lower())
        if usuario is None:
            _verificar(_hash_de_relleno(), contrasena)  # tarda lo mismo que con un usuario real
            error = _CREDENCIALES_INVALIDAS
        elif usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            minutos = int((usuario.bloqueado_hasta - ahora).total_seconds() // 60) + 1
            error = ErrorDeNegocio("cuenta_bloqueada",
                                   f"Demasiados intentos fallidos. Reintentá en {minutos} minutos.")
        elif not _verificar(usuario.password_hash, contrasena):
            usuarios.registrar_fallo(tx, usuario.id, ahora, INTENTOS_MAX, timedelta(minutes=BLOQUEO_MINUTOS))
            error = _CREDENCIALES_INVALIDAS
        else:
            token = secrets.token_urlsafe(32)
            usuarios.reiniciar_intentos(tx, usuario.id)
            sesiones.borrar_vencidas(tx, ahora)
            sesiones.crear(tx, usuario.id, _hash_token(token), ahora + timedelta(hours=SESION_HORAS))
    if error:
        raise error
    return token, usuario


def usuario_de_sesion(token: Optional[str]) -> Usuario:
    if not token:
        raise _NO_AUTENTICADO
    with transaccion() as tx:
        usuario = sesiones.usuario_de_token(tx, _hash_token(token), _ahora())
    if usuario is None:
        raise _NO_AUTENTICADO
    return usuario


def cerrar_sesion(token: Optional[str]) -> None:
    if token:
        with transaccion() as tx:
            sesiones.borrar(tx, _hash_token(token))


def cambiar_contrasena(usuario: Usuario, token: str, actual: str, nueva: str) -> None:
    """
    Cambia la contraseña del usuario de la sesión y cierra sus demás sesiones.
    Una contraseña actual incorrecta suma al contador de fallos del login, así que a los
    INTENTOS_MAX la cuenta se bloquea; el error se lanza fuera de la transacción para que quede.
    """
    ahora = _ahora()
    error: Optional[ErrorDeNegocio] = None
    with transaccion() as tx:
        # Se relee: el usuario de la dependencia podría estar desactualizado (otro intento simultáneo)
        usuario = usuarios.buscar_por_email(tx, usuario.email)
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            minutos = int((usuario.bloqueado_hasta - ahora).total_seconds() // 60) + 1
            error = ErrorDeNegocio("cuenta_bloqueada",
                                   f"Demasiados intentos fallidos. Reintentá en {minutos} minutos.")
        elif not _verificar(usuario.password_hash, actual):
            usuarios.registrar_fallo(tx, usuario.id, ahora, INTENTOS_MAX, timedelta(minutes=BLOQUEO_MINUTOS))
            error = ErrorDeNegocio("contrasena_actual_incorrecta", "La contraseña actual no es correcta.")
        else:
            validar_contrasena(nueva)  # si falla, revierte la transacción: no hay nada que guardar
            if _verificar(usuario.password_hash, nueva):
                raise ErrorDeNegocio("contrasena_repetida",
                                     "La contraseña nueva tiene que ser distinta de la actual.")
            usuarios.cambiar_contrasena(tx, usuario.id, _hasher.hash(nueva))
            sesiones.borrar_las_demas(tx, usuario.id, _hash_token(token))
    if error:
        raise error


def resetear_contrasena(email: str, nueva: str) -> Usuario:
    """Para el admin (por comando): contraseña nueva, cuenta desbloqueada y todas sus sesiones cerradas."""
    validar_contrasena(nueva)
    with transaccion() as tx:
        usuario = usuarios.buscar_por_email(tx, email.strip().lower())
        if usuario is None:
            raise ErrorDeNegocio("usuario_no_encontrado", "No existe una cuenta con ese email.")
        usuarios.cambiar_contrasena(tx, usuario.id, _hasher.hash(nueva))
        sesiones.borrar_las_demas(tx, usuario.id, None)
    return usuario


def crear_admin(email: str, nombre: str, contrasena: str) -> Tuple[Usuario, bool]:
    """Crea un admin, o promueve a uno existente (en ese caso la contraseña se ignora).
    Devuelve el usuario y si ya existía."""
    validar_contrasena(contrasena)
    email = email.strip().lower()
    with transaccion() as tx:
        existente = usuarios.buscar_por_email(tx, email)
        if existente:
            usuarios.marcar_admin(tx, existente.id)
            return existente.model_copy(update={"es_admin": True}), True
        # Los admin se crean por comando: el aviso de uso no profesional se registra con la fecha de alta
        nuevo = usuarios.crear(tx, email, _hasher.hash(contrasena), nombre, "investigador",
                               es_admin=True, aviso_aceptado_en=_ahora())
    return nuevo, False
