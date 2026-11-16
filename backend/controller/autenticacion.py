"""
Registro, inicio y cierre de sesión, verificación del email y recuperación de la contraseña.

La sesión es un token aleatorio que viaja en una cookie; en la base solo se guarda su hash,
así que leer la tabla `sesion` no alcanza para usar una sesión. Los enlaces que van por mail
(decisión 030) siguen la misma idea.
"""

import hashlib
import logging
import secrets
import threading
from datetime import datetime, timedelta, timezone
from functools import cache
from typing import Optional, Tuple

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from backend.configuracion import BLOQUEO_MINUTOS, INTENTOS_MAX, SESION_HORAS, URL_PUBLICA
from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import RegistroInput, Usuario
from backend.datos import enlaces, sesiones, usuarios
from backend.datos.conexion import transaccion
from backend.services import correo

logger = logging.getLogger(__name__)

_hasher = PasswordHasher()  # argon2id

_CREDENCIALES_INVALIDAS = ErrorDeNegocio("credenciales_invalidas", "Email o contraseña incorrectos.")
_NO_AUTENTICADO = ErrorDeNegocio("no_autenticado", "Tenés que iniciar sesión.")
_ENLACE_INVALIDO = ErrorDeNegocio("enlace_invalido", "El enlace venció o ya se usó. Pedí uno nuevo.")

# RN15 y RN16: vigencia de cada enlace
VIGENCIA = {"verificacion": timedelta(hours=24), "recuperacion": timedelta(hours=1)}


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


def _nuevo_enlace(tx, usuario_id, tipo: str) -> str:
    token = secrets.token_urlsafe(32)
    enlaces.reemplazar(tx, usuario_id, tipo, _hash_token(token), _ahora() + VIGENCIA[tipo])
    return token


def _mail_verificacion(email: str, token: str) -> None:
    correo.enviar(email, "Confirmá tu email - Laboratorio Virtual Auditivo",
                  "Para confirmar tu email y poder pedir simulaciones, abrí este enlace "
                  f"(vence en 24 horas):\n\n{URL_PUBLICA}/verificar?token={token}\n\n"
                  "Si no creaste una cuenta, ignorá este mail.")


def _mail_recuperacion(email: str, token: str) -> None:
    correo.enviar(email, "Recuperar tu contraseña - Laboratorio Virtual Auditivo",
                  "Para elegir una contraseña nueva, abrí este enlace (vence en 1 hora y sirve una sola vez):"
                  f"\n\n{URL_PUBLICA}/recuperar?token={token}\n\n"
                  "Si no lo pediste, ignorá este mail: tu contraseña sigue igual.")


def _en_segundo_plano(enviar, email: str, token: str) -> None:
    """El pedido no espera al servidor de mail: además, si tardara solo con emails existentes,
    el tiempo de respuesta revelaría quién está registrado (RN16). Un fallo queda en el log."""
    def tarea():
        try:
            enviar(email, token)
        except Exception:
            logger.exception("No se pudo enviar el mail a %s", email)
    threading.Thread(target=tarea, daemon=True).start()


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
        token = _nuevo_enlace(tx, usuario.id, "verificacion") if usuario else ""
    if usuario is None:
        raise ErrorDeNegocio("email_ya_registrado", "Ya existe una cuenta con ese email.")
    _en_segundo_plano(_mail_verificacion, usuario.email, token)
    return usuario


def reenviar_verificacion(usuario: Usuario) -> None:
    if usuario.email_verificado:
        raise ErrorDeNegocio("email_ya_verificado", "Tu email ya está confirmado.")
    with transaccion() as tx:
        token = _nuevo_enlace(tx, usuario.id, "verificacion")
    try:
        _mail_verificacion(usuario.email, token)
    except Exception:
        logger.exception("No se pudo enviar el mail a %s", usuario.email)
        raise ErrorDeNegocio("mail_no_enviado", "No pudimos enviar el mail. Reintentá en unos minutos.")


def verificar_email(token: str) -> None:
    """RN15."""
    ahora = _ahora()
    with transaccion() as tx:
        usuario = enlaces.usar(tx, "verificacion", _hash_token(token), ahora)
        if usuario is None:
            raise _ENLACE_INVALIDO
        usuarios.marcar_verificado(tx, usuario.id, ahora)


def pedir_recuperacion(email: str) -> None:
    """RN16: no dice si el email existe; solo le llega el mail a quien tiene cuenta. Sin SMTP el mail
    no sale, así que el pedido va directo al admin; con SMTP, solo si el usuario avisa (decisión 028)."""
    with transaccion() as tx:
        usuario = usuarios.buscar_por_email(tx, email.strip().lower())
        token = _nuevo_enlace(tx, usuario.id, "recuperacion") if usuario else ""
        if usuario and not correo.configurado():
            usuarios.pedir_restablecimiento(tx, usuario.id, _ahora())
    if usuario:
        _en_segundo_plano(_mail_recuperacion, usuario.email, token)


def avisar_al_admin(email: str) -> None:
    """El mail de recuperación no llegó: deja el pedido en el panel de admin (decisión 028).
    Como RN16, no dice si el email existe."""
    with transaccion() as tx:
        usuario = usuarios.buscar_por_email(tx, email.strip().lower())
        if usuario:
            usuarios.pedir_restablecimiento(tx, usuario.id, _ahora())


def recuperar_contrasena(token: str, nueva: str) -> None:
    """RN16: contraseña nueva, cuenta desbloqueada y todas sus sesiones cerradas. Usar el enlace
    prueba que recibe el mail, así que también verifica el email."""
    validar_contrasena(nueva)  # antes de usar el enlace: una contraseña inválida no lo gasta
    ahora = _ahora()
    with transaccion() as tx:
        usuario = enlaces.usar(tx, "recuperacion", _hash_token(token), ahora)
        if usuario is None:
            raise _ENLACE_INVALIDO
        usuarios.cambiar_contrasena(tx, usuario.id, _hasher.hash(nueva))
        usuarios.marcar_verificado(tx, usuario.id, ahora)
        sesiones.borrar_las_demas(tx, usuario.id, None)


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
    """Para el admin (comando o contraseña temporal del panel): contraseña nueva, cuenta desbloqueada y
    todas sus sesiones cerradas. El usuario tendrá que elegir otra al entrar (decisión 031)."""
    validar_contrasena(nueva)
    with transaccion() as tx:
        usuario = usuarios.buscar_por_email(tx, email.strip().lower())
        if usuario is None:
            raise ErrorDeNegocio("usuario_no_encontrado", "No existe una cuenta con ese email.")
        usuarios.cambiar_contrasena(tx, usuario.id, _hasher.hash(nueva), temporal=True)
        sesiones.borrar_las_demas(tx, usuario.id, None)
    return usuario


def exigir_contrasena_definitiva(usuario: Usuario) -> None:
    """Con una contraseña que conoce un admin, solo se puede elegir una nueva (decisión 031)."""
    if usuario.debe_cambiar_contrasena:
        raise ErrorDeNegocio("debe_cambiar_contrasena", "Elegí una contraseña nueva para seguir.")


def elegir_contrasena(usuario: Usuario, token: Optional[str], nueva: str) -> None:
    """Después de entrar con una contraseña temporal: no pide la actual, porque acaba de usarla."""
    if not usuario.debe_cambiar_contrasena:
        raise ErrorDeNegocio("sin_contrasena_temporal",
                             "Tu contraseña no es temporal: cambiala desde Mi cuenta.")
    validar_contrasena(nueva)
    if _verificar(usuario.password_hash, nueva):
        raise ErrorDeNegocio("contrasena_repetida",
                             "La contraseña nueva tiene que ser distinta de la temporal.")
    with transaccion() as tx:
        usuarios.cambiar_contrasena(tx, usuario.id, _hasher.hash(nueva))
        sesiones.borrar_las_demas(tx, usuario.id, _hash_token(token) if token else None)


def crear_admin(email: str, nombre: str, contrasena: str) -> Tuple[Usuario, bool]:
    """Crea un admin, o promueve a uno existente (en ese caso la contraseña se ignora).
    Devuelve el usuario y si ya existía."""
    validar_contrasena(contrasena)
    email = email.strip().lower()
    with transaccion() as tx:
        existente = usuarios.buscar_por_email(tx, email)
        if existente:
            usuarios.marcar_admin(tx, existente.id, _ahora())
            return existente.model_copy(update={"es_admin": True}), True
        # Los admin se crean por comando: el aviso de uso no profesional y el email (RN15) quedan
        # aceptado y verificado con la fecha de alta
        nuevo = usuarios.crear(tx, email, _hasher.hash(contrasena), nombre, "investigador",
                               es_admin=True, aviso_aceptado_en=_ahora(), email_verificado_en=_ahora())
    return nuevo, False
