"""debe cambiar contrasena

Revision ID: e5c3a9b1d7f2
Revises: d2b7f0a4c8e1
Create Date: 2026-11-16 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5c3a9b1d7f2'
down_revision: Union[str, Sequence[str], None] = 'd2b7f0a4c8e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # server_default: las cuentas que ya existen quedan sin cambio pendiente
    op.add_column('usuario', sa.Column('debe_cambiar_contrasena', sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('usuario', 'debe_cambiar_contrasena')
