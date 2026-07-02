"""corrige tipo conta destino

Revision ID: a1b2c3d4e5f6
Revises: 19de743140b4
Create Date: 2026-07-02 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '19de743140b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        sa.text(
            "UPDATE vendas SET tipo_conta_destino = 'MAQUININHA_TON' "
            "WHERE tipo_conta_destino = 'MAQUINHINHA_TON' OR tipo_conta_destino IS NULL"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text(
            "UPDATE vendas SET tipo_conta_destino = 'MAQUINHINHA_TON' "
            "WHERE tipo_conta_destino = 'MAQUININHA_TON'"
        )
    )