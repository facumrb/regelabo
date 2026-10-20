"""
Acceso a los usuarios. Todas las funciones reciben la sesión de `transaccion()`
y devuelven objetos de negocio, nunca filas de la base.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import case, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.controller.modelos import Usuario
from backend.datos.tablas import Usuario as UsuarioFila


def buscar_por_email(tx: Session, email: str) -> Optional[Usuario]:
    fila = tx.scalars(select(UsuarioFila).where(UsuarioFila.email == email)).first()
    return Usuario.model_validate(fila) if fila else None


def crear(tx: Session, email: str, password_hash: str, nombre: str, tipo_perfil: str,
          es_admin: bool, aviso_aceptado_en: datetime) -> Optional[Usuario]:
    """Crea el usuario; devuelve None si el email ya existe."""
    fila = UsuarioFila(email=email, password_hash=password_hash, nombre=nombre,
                       tipo_perfil=tipo_perfil, es_admin=es_admin, aviso_aceptado_en=aviso_aceptado_en)
    try:
        with tx.begin_nested():  # savepoint: el choque con el email único no arruina la transacción
            tx.add(fila)
    except IntegrityError:
        return None
    return Usuario.model_validate(fila)


def bloquear(tx: Session, usuario_id: UUID) -> None:
    """Bloquea la fila del usuario hasta el fin de la transacción: dos pedidos suyos se hacen en fila."""
    tx.execute(select(UsuarioFila.id).where(UsuarioFila.id == usuario_id).with_for_update())


def marcar_admin(tx: Session, usuario_id: UUID) -> None:
    tx.execute(update(UsuarioFila).where(UsuarioFila.id == usuario_id).values(es_admin=True))


def registrar_fallo(tx: Session, usuario_id: UUID, ahora: datetime, intentos_max: int,
                    bloqueo: timedelta) -> None:
    """
    Suma un intento fallido. Al llegar al máximo bloquea la cuenta y reinicia el contador.
    Es un solo UPDATE, así que dos intentos simultáneos no se pisan.
    """
    llega_al_maximo = UsuarioFila.intentos_fallidos + 1 >= intentos_max
    tx.execute(
        update(UsuarioFila).where(UsuarioFila.id == usuario_id).values(
            intentos_fallidos=case((llega_al_maximo, 0), else_=UsuarioFila.intentos_fallidos + 1),
            bloqueado_hasta=case((llega_al_maximo, ahora + bloqueo), else_=UsuarioFila.bloqueado_hasta),
        )
    )


def cambiar_contrasena(tx: Session, usuario_id: UUID, password_hash: str) -> None:
    """Guarda el hash nuevo y desbloquea la cuenta."""
    tx.execute(update(UsuarioFila).where(UsuarioFila.id == usuario_id)
               .values(password_hash=password_hash, intentos_fallidos=0, bloqueado_hasta=None))


def reiniciar_intentos(tx: Session, usuario_id: UUID) -> None:
    tx.execute(update(UsuarioFila).where(UsuarioFila.id == usuario_id)
               .values(intentos_fallidos=0, bloqueado_hasta=None))
