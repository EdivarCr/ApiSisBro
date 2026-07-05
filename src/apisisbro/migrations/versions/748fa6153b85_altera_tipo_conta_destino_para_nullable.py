"""altera_tipo_conta_destino_para_nullable

Revision ID: 748fa6153b85
Revises: b0f0607fc4b2
Create Date: 2026-07-03 00:11:45.568941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '748fa6153b85'
down_revision: Union[str, Sequence[str], None] = 'b0f0607fc4b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Altera a coluna para aceitar valores nulos (vendas PENDENTES)."""
    op.alter_column(
        'vendas',
        'tipo_conta_destino',
        existing_type=sa.String(length=20),
        nullable=True
    )


def downgrade() -> None:
    """Volta a tornar a coluna obrigatória (Cuidado: falhará se houver registros nulos)."""
    op.alter_column(
        'vendas',
        'tipo_conta_destino',
        existing_type=sa.String(length=20),
        nullable=False
    )
