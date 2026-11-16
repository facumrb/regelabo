"""comparativas guardadas

Revision ID: f7a2c4e6b9d1
Revises: e5c3a9b1d7f2
Create Date: 2026-11-16 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7a2c4e6b9d1'
down_revision: Union[str, Sequence[str], None] = 'e5c3a9b1d7f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('comparativa',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('usuario_id', sa.Uuid(), nullable=False),
    sa.Column('caso_id', sa.Uuid(), nullable=True),
    sa.Column('titulo', sa.String(length=100), nullable=False),
    sa.Column('notas', sa.Text(), nullable=True),
    sa.Column('borrado_en', sa.DateTime(timezone=True), nullable=True),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['caso_id'], ['caso.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comparativa_caso_id'), 'comparativa', ['caso_id'], unique=False)
    op.create_index(op.f('ix_comparativa_usuario_id'), 'comparativa', ['usuario_id'], unique=False)
    op.create_table('comparativa_simulacion',
    sa.Column('comparativa_id', sa.Uuid(), nullable=False),
    sa.Column('simulacion_id', sa.Uuid(), nullable=False),
    sa.Column('orden', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['comparativa_id'], ['comparativa.id'], ),
    sa.ForeignKeyConstraint(['simulacion_id'], ['simulacion.id'], ),
    sa.PrimaryKeyConstraint('comparativa_id', 'simulacion_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('comparativa_simulacion')
    op.drop_index(op.f('ix_comparativa_usuario_id'), table_name='comparativa')
    op.drop_index(op.f('ix_comparativa_caso_id'), table_name='comparativa')
    op.drop_table('comparativa')
