"""pedido de restablecimiento

Revision ID: d2b7f0a4c8e1
Revises: c4a1e2d9f310
Create Date: 2026-11-16 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2b7f0a4c8e1'
down_revision: Union[str, Sequence[str], None] = 'c4a1e2d9f310'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('usuario', sa.Column('restablecimiento_pedido_en', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('usuario', 'restablecimiento_pedido_en')
