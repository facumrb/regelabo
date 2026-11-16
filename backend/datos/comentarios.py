"""
Acceso a los comentarios (RN13). Al listarlos se suman los datos del autor, que el admin
usa para filtrar por tipo de usuario.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.controller.modelos import Comentario, TipoPerfil
from backend.datos.tablas import Comentario as ComentarioFila
from backend.datos.tablas import Usuario as UsuarioFila


def _comentario(fila: ComentarioFila, autor: UsuarioFila) -> Comentario:
    return Comentario(id=fila.id, texto=fila.texto, estado=fila.estado, creado_en=fila.creado_en,
                      autor_nombre=autor.nombre, autor_email=autor.email, autor_tipo=autor.tipo_perfil)


def crear(tx: Session, usuario_id: UUID, texto: str) -> None:
    tx.add(ComentarioFila(usuario_id=usuario_id, texto=texto))


def listar(tx: Session, limite: int, despues_de: Optional[UUID], estados: List[str],
           tipo: Optional[TipoPerfil]) -> List[Comentario]:
    """Del más nuevo al más viejo, paginado por cursor (ids UUIDv7, como en `casos.py`)."""
    consulta = (select(ComentarioFila, UsuarioFila)
                .join(UsuarioFila, ComentarioFila.usuario_id == UsuarioFila.id)
                .where(ComentarioFila.estado.in_(estados))
                .order_by(ComentarioFila.id.desc()).limit(limite))
    if tipo:
        consulta = consulta.where(UsuarioFila.tipo_perfil == tipo)
    if despues_de:
        consulta = consulta.where(ComentarioFila.id < despues_de)
    return [_comentario(c, u) for c, u in tx.execute(consulta)]


def cambiar_estado(tx: Session, comentario_id: UUID, estado: str) -> Optional[Comentario]:
    """Devuelve None si el comentario no existe."""
    fila = tx.get(ComentarioFila, comentario_id)
    if fila is None:
        return None
    fila.estado = estado
    return _comentario(fila, tx.get(UsuarioFila, fila.usuario_id))


def contar_nuevos(tx: Session) -> int:
    return tx.scalar(select(func.count()).where(ComentarioFila.estado == "nuevo"))
