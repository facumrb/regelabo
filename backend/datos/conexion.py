"""
Conexión a la base de datos.

La URL se lee de la variable de entorno DATABASE_URL. En desarrollo se toma del
archivo `.env` de la raíz (ver `.env.example`); en producción la define el servidor.
"""

import os
from contextlib import contextmanager
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Ruta explícita: la búsqueda automática de python-dotenv falla cuando Alembic carga este módulo
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

engine = create_engine(os.environ["DATABASE_URL"])


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
