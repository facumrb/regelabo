"""
Configuración de Alembic: usa la misma conexión (DATABASE_URL) y las mismas tablas que la app.
"""

from logging.config import fileConfig

from alembic import context

from backend.datos.conexion import engine
from backend.datos.tablas import Base

if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
