"""cria tipo conta destino

Revision ID: 19de743140b4
Revises: 3721740b4f9c
Create Date: 2026-07-02 21:31:15.999328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19de743140b4'
down_revision: Union[str, Sequence[str], None] = '3721740b4f9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'vendas',
        sa.Column(
            'tipo_conta_destino',
            sa.String(length=20),
            nullable=True,
            server_default=sa.text("'MAQUINHINHA_TON'"),
        ),
    )
    op.execute(
        sa.text(
            "UPDATE vendas SET tipo_conta_destino = 'MAQUINHINHA_TON' "
            "WHERE tipo_conta_destino IS NULL"
        )
    )
    op.alter_column(
        'vendas',
        'tipo_conta_destino',
        nullable=False,
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('vendas', 'tipo_conta_destino')
