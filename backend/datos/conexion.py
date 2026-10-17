"""
Conexión a la base de datos.

La URL sale de `backend.configuracion` (variable de entorno DATABASE_URL).
"""

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.configuracion import DATABASE_URL

engine = create_engine(DATABASE_URL)


@contextmanager
def transaccion() -> Iterator[Session]:
    """
    Abre una transacción: se confirma al salir del bloque y se revierte si hay una excepción.

    El controller la usa cuando varias operaciones de datos tienen que guardarse juntas
    (por ejemplo, verificar el cupo y encolar una simulación) y le pasa la sesión a cada
    función de `datos/`. Nunca ejecuta consultas por su cuenta.
    """
    with Session(engine) as sesion, sesion.begin():
        yield sesion
