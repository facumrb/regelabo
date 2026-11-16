"""
Audiogramas guardados en un caso (decisión 032). Como en `casos.py`, solo se ven los de casos
propios y no borrados (RN4).
"""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.controller.modelos import AudiogramaGuardado, AudiogramPoint
from backend.datos.tablas import Audiograma as AudiogramaFila
from backend.datos.tablas import Caso as CasoFila
from backend.datos.tablas import PuntoAudiograma as PuntoFila

# En la tabla el patrón con caída en agudos se llama "pendiente" (esquema de la decisión 010)
_PATRON_A_TABLA = {"plano": "plano", "caida_en_agudos": "pendiente"}
_PATRON_DE_TABLA = {v: k for k, v in _PATRON_A_TABLA.items()}


def crear(tx: Session, caso_id: UUID, origen: str, pta_db: float, gravedad: str, patron: str, perfil: str,
          puntos: List[AudiogramPoint]) -> UUID:
    fila = AudiogramaFila(caso_id=caso_id, origen=origen, pta_db=pta_db, gravedad=gravedad,
                          patron=_PATRON_A_TABLA[patron], perfil=perfil)
    tx.add(fila)
    tx.flush()  # completa el id
    tx.add_all(PuntoFila(audiograma_id=fila.id, frecuencia_hz=p.frequency, perdida_db=p.hearing_loss_db)
               for p in puntos)
    return fila.id


def listar(tx: Session, caso_id: UUID, usuario_id: UUID) -> List[AudiogramaGuardado]:
    """Del más nuevo al más viejo, con sus puntos ordenados por frecuencia."""
    filas = tx.scalars(
        select(AudiogramaFila).join(CasoFila, AudiogramaFila.caso_id == CasoFila.id)
        .where(AudiogramaFila.caso_id == caso_id, CasoFila.usuario_id == usuario_id,
               CasoFila.borrado_en.is_(None))
        .order_by(AudiogramaFila.id.desc())
    ).all()
    puntos = tx.scalars(select(PuntoFila).where(PuntoFila.audiograma_id.in_([f.id for f in filas]))
                        .order_by(PuntoFila.frecuencia_hz)).all()
    return [AudiogramaGuardado(
        id=f.id, creado_en=f.creado_en, origen=f.origen, pta_db=f.pta_db, gravedad=f.gravedad,
        patron=_PATRON_DE_TABLA[f.patron], perfil=f.perfil,
        puntos=[AudiogramPoint(frequency=p.frecuencia_hz, hearing_loss_db=p.perdida_db)
                for p in puntos if p.audiograma_id == f.id],
    ) for f in filas]
