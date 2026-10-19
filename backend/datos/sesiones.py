"""
Acceso a las sesiones. En la base solo se guarda el hash del token de la cookie.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.controller.modelos import Usuario
from backend.datos.tablas import Sesion
from backend.datos.tablas import Usuario as UsuarioFila


def crear(tx: Session, usuario_id: UUID, token_hash: str, expira_en: datetime) -> None:
    tx.add(Sesion(usuario_id=usuario_id, token_hash=token_hash, expira_en=expira_en))


def usuario_de_token(tx: Session, token_hash: str, ahora: datetime) -> Optional[Usuario]:
    """El usuario dueño de una sesión vigente, o None."""
    fila = tx.scalars(
        select(UsuarioFila).join(Sesion, Sesion.usuario_id == UsuarioFila.id)
        .where(Sesion.token_hash == token_hash, Sesion.expira_en > ahora)
    ).first()
    return Usuario.model_validate(fila) if fila else None


def borrar(tx: Session, token_hash: str) -> None:
    tx.execute(delete(Sesion).where(Sesion.token_hash == token_hash))


def borrar_las_demas(tx: Session, usuario_id: UUID, token_hash_actual: Optional[str]) -> None:
    """Cierra todas las sesiones del usuario salvo la actual (con None, todas)."""
    consulta = delete(Sesion).where(Sesion.usuario_id == usuario_id)
    if token_hash_actual:
        consulta = consulta.where(Sesion.token_hash != token_hash_actual)
    tx.execute(consulta)


def borrar_vencidas(tx: Session, ahora: datetime) -> None:
    tx.execute(delete(Sesion).where(Sesion.expira_en <= ahora))
