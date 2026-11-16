"""
Comparativas guardadas (decisión 025). Como en `casos.py`: todas las consultas filtran por dueño y
excluyen las borradas (RN4).
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.controller.modelos import Comparativa, ComparativaDatos, ComparativaInput
from backend.datos.tablas import Comparativa as ComparativaFila
from backend.datos.tablas import ComparativaSimulacion as ItemFila


def _visibles(usuario_id: UUID):
    return select(ComparativaFila).where(ComparativaFila.usuario_id == usuario_id,
                                         ComparativaFila.borrado_en.is_(None))


def _comparativas(tx: Session, filas: List[ComparativaFila]) -> List[Comparativa]:
    items = tx.scalars(select(ItemFila).where(ItemFila.comparativa_id.in_([f.id for f in filas]))
                       .order_by(ItemFila.orden)).all()
    return [Comparativa(id=f.id, creado_en=f.creado_en, titulo=f.titulo, notas=f.notas, caso_id=f.caso_id,
                        simulacion_ids=[i.simulacion_id for i in items if i.comparativa_id == f.id])
            for f in filas]


def crear(tx: Session, usuario_id: UUID, datos: ComparativaInput) -> Comparativa:
    fila = ComparativaFila(usuario_id=usuario_id, titulo=datos.titulo, notas=datos.notas,
                           caso_id=datos.caso_id)
    tx.add(fila)
    tx.flush()  # completa id y creado_en
    tx.add_all(ItemFila(comparativa_id=fila.id, simulacion_id=s, orden=i)
               for i, s in enumerate(datos.simulacion_ids))
    tx.flush()
    return _comparativas(tx, [fila])[0]


def listar(tx: Session, usuario_id: UUID, limite: int, despues_de: Optional[UUID],
           caso_id: Optional[UUID]) -> List[Comparativa]:
    """De la más nueva a la más vieja, paginado por cursor (ids UUIDv7)."""
    consulta = _visibles(usuario_id).order_by(ComparativaFila.id.desc()).limit(limite)
    if caso_id:
        consulta = consulta.where(ComparativaFila.caso_id == caso_id)
    if despues_de:
        consulta = consulta.where(ComparativaFila.id < despues_de)
    return _comparativas(tx, list(tx.scalars(consulta)))


def buscar(tx: Session, comparativa_id: UUID, usuario_id: UUID) -> Optional[Comparativa]:
    fila = tx.scalars(_visibles(usuario_id).where(ComparativaFila.id == comparativa_id)).first()
    return _comparativas(tx, [fila])[0] if fila else None


def actualizar(tx: Session, comparativa_id: UUID, usuario_id: UUID,
               datos: ComparativaDatos) -> Optional[Comparativa]:
    """Título, notas y caso; las simulaciones no cambian. None si no existe para este usuario."""
    fila = tx.scalars(_visibles(usuario_id).where(ComparativaFila.id == comparativa_id)).first()
    if fila is None:
        return None
    fila.titulo, fila.notas, fila.caso_id = datos.titulo, datos.notas, datos.caso_id
    return _comparativas(tx, [fila])[0]


def borrar(tx: Session, comparativa_id: UUID, usuario_id: UUID, ahora: datetime) -> bool:
    """Borrado lógico. False si no existe para este usuario."""
    resultado = tx.execute(
        update(ComparativaFila)
        .where(ComparativaFila.id == comparativa_id, ComparativaFila.usuario_id == usuario_id,
               ComparativaFila.borrado_en.is_(None))
        .values(borrado_en=ahora)
    )
    return resultado.rowcount == 1
