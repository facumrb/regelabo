"""
Configuración de los tests.

Corren contra PostgreSQL real, pero en una base aparte (`<nombre>_test`) que se crea sola:
nunca tocan la base de desarrollo. Las tablas salen de las migraciones de Alembic.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# Antes de importar nada de backend: DATABASE_URL tiene que apuntar a la base de test
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
_url = make_url(os.environ["DATABASE_URL"])
if not _url.database.endswith("_test"):
    _url = _url.set(database=f"{_url.database}_test")
os.environ["DATABASE_URL"] = _url.render_as_string(hide_password=False)
os.environ["COOKIE_SECURE"] = "false"  # el cliente de test usa http

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from backend.datos.conexion import engine  # noqa: E402
from backend.views import crear_app  # noqa: E402
from backend.views.limites import limiter  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def base_de_test():
    assert engine.url.database.endswith("_test"), "los tests no pueden correr contra otra base"
    admin = create_engine(engine.url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conexion:
        existe = conexion.scalar(text("SELECT 1 FROM pg_database WHERE datname = :n"),
                                 {"n": engine.url.database})
        if not existe:
            conexion.execute(text(f'CREATE DATABASE "{engine.url.database}"'))
    admin.dispose()
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
def tablas_vacias(base_de_test):
    with engine.begin() as conexion:
        conexion.execute(text(
            "TRUNCATE usuario, sesion, caso, audiograma, punto_audiograma, resultado_simulacion, "
            "simulacion, arquetipo, registro_abr, comparacion CASCADE"))


@pytest.fixture(autouse=True)
def sin_limite_de_pedidos():
    limiter.enabled = False
    limiter.reset()
    yield
    limiter.enabled = False


@pytest.fixture
def cliente():
    """Un navegador: guarda sus propias cookies. Dos clientes son dos ventanas independientes."""
    return TestClient(crear_app())


@pytest.fixture
def registro_valido():
    return {"email": "ana@example.com", "password": "una-clave-larga", "nombre": "Ana",
            "tipo_perfil": "estudiante", "acepta_aviso": True}
