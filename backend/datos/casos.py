"""
Acceso a los casos. Todas las consultas filtran por dueño y excluyen los borrados:
así un caso ajeno o borrado es, para el resto del sistema, un caso que no existe (RN4).
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.controller.modelos import Caso, CasoInput
from backend.datos.tablas import Caso as CasoFila


def _visibles(usuario_id: UUID):
    return select(CasoFila).where(CasoFila.usuario_id == usuario_id, CasoFila.borrado_en.is_(None))


def crear(tx: Session, usuario_id: UUID, datos: CasoInput) -> Caso:
    fila = CasoFila(usuario_id=usuario_id, **datos.model_dump())
    tx.add(fila)
    tx.flush()  # completa id y creado_en
    return Caso.model_validate(fila)


def listar(tx: Session, usuario_id: UUID, limite: int, despues_de: Optional[UUID]) -> List[Caso]:
    """
    Del más nuevo al más viejo. Paginación por cursor: los ids son UUIDv7 (ordenados por
    tiempo), así que la página siguiente son los ids menores que el último recibido.
    """
    consulta = _visibles(usuario_id).order_by(CasoFila.id.desc()).limit(limite)
    if despues_de:
        consulta = consulta.where(CasoFila.id < despues_de)
    return [Caso.model_validate(f) for f in tx.scalars(consulta)]


def buscar(tx: Session, caso_id: UUID, usuario_id: UUID) -> Optional[Caso]:
    fila = tx.scalars(_visibles(usuario_id).where(CasoFila.id == caso_id)).first()
    return Caso.model_validate(fila) if fila else None


def actualizar(tx: Session, caso_id: UUID, usuario_id: UUID, datos: CasoInput) -> Optional[Caso]:
    """Devuelve None si el caso no existe para este usuario."""
    fila = tx.scalars(_visibles(usuario_id).where(CasoFila.id == caso_id)).first()
    if fila is None:
        return None
    for campo, valor in datos.model_dump().items():
        setattr(fila, campo, valor)
    return Caso.model_validate(fila)


def borrar(tx: Session, caso_id: UUID, usuario_id: UUID, ahora: datetime) -> bool:
    """Borrado lógico. Devuelve False si el caso no existe para este usuario."""
    resultado = tx.execute(
        update(CasoFila)
        .where(CasoFila.id == caso_id, CasoFila.usuario_id == usuario_id, CasoFila.borrado_en.is_(None))
        .values(borrado_en=ahora)
    )
    return resultado.rowcount == 1
