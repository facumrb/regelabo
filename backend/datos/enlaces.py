"""
Enlaces de un solo uso enviados por mail (decisión 030). En la base solo se guarda el hash del token.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.orm import Session

from backend.controller.modelos import Usuario
from backend.datos.tablas import EnlaceEmail
from backend.datos.tablas import Usuario as UsuarioFila


def reemplazar(tx: Session, usuario_id: UUID, tipo: str, token_hash: str, expira_en: datetime) -> None:
    """Guarda un enlace nuevo y borra los anteriores del mismo tipo: solo sirve el último mail."""
    tx.execute(delete(EnlaceEmail).where(EnlaceEmail.usuario_id == usuario_id, EnlaceEmail.tipo == tipo))
    tx.add(EnlaceEmail(usuario_id=usuario_id, tipo=tipo, token_hash=token_hash, expira_en=expira_en))


def usar(tx: Session, tipo: str, token_hash: str, ahora: datetime) -> Optional[Usuario]:
    """Borra el enlace y devuelve su usuario si estaba vigente; None si no existe o venció.
    El DELETE ... RETURNING hace que dos pedidos simultáneos no puedan usar el mismo enlace."""
    usuario_id = tx.scalar(
        delete(EnlaceEmail)
        .where(EnlaceEmail.tipo == tipo, EnlaceEmail.token_hash == token_hash, EnlaceEmail.expira_en > ahora)
        .returning(EnlaceEmail.usuario_id)
    )
    if usuario_id is None:
        return None
    return Usuario.model_validate(tx.get(UsuarioFila, usuario_id))
