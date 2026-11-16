"""tabla comentario

Revision ID: c4a1e2d9f310
Revises: b8f7d8bc69b7
Create Date: 2026-11-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4a1e2d9f310'
down_revision: Union[str, Sequence[str], None] = 'b8f7d8bc69b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('comentario',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('usuario_id', sa.Uuid(), nullable=False),
    sa.Column('texto', sa.Text(), nullable=False),
    sa.Column('estado', sa.Enum('nuevo', 'leido', 'archivado', name='estado_comentario', native_enum=False, create_constraint=True, length=20), nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comentario_usuario_id'), 'comentario', ['usuario_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_comentario_usuario_id'), table_name='comentario')
    op.drop_table('comentario')
