"""sexo del caso con valores fijos

Revision ID: 56acda104db1
Revises: 7c13713aaa68
Create Date: 2026-10-16 19:12:59.525359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56acda104db1'
down_revision: Union[str, Sequence[str], None] = '7c13713aaa68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Escrita a mano: autogenerate no detecta CHECK nuevos. El nombre sigue al de los otros
# campos de valores fijos (el `name` de sa.Enum).

def upgrade() -> None:
    op.execute("UPDATE caso SET sexo = NULL WHERE sexo NOT IN ('femenino', 'masculino', 'otro')")
    op.create_check_constraint("sexo", "caso", "sexo IN ('femenino', 'masculino', 'otro')")


def downgrade() -> None:
    op.drop_constraint("sexo", "caso", type_="check")
