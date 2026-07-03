"""corrige_typo_maquininha_ton

Revision ID: b0f0607fc4b2
Revises: 19de743140b4
Create Date: 2026-07-02 23:58:07.599892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0f0607fc4b2'
down_revision: Union[str, Sequence[str], None] = '19de743140b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE vendas SET tipo_conta_destino = 'MAQUININHA_TON' WHERE tipo_conta_destino = 'MAQUINHINHA_TON';"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE vendas SET tipo_conta_destino = 'MAQUINHINHA_TON' WHERE tipo_conta_destino = 'MAQUININHA_TON';"
    )