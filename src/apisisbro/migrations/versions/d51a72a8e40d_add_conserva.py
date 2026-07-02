"""add conserva

Revision ID: d51a72a8e40d
Revises: 88bb5a9979dd
Create Date: 2026-05-08 03:19:41.538380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd51a72a8e40d'
down_revision: Union[str, Sequence[str], None] = '88bb5a9979dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. O Postgres não permite ALTER TYPE dentro de blocos de transação comuns
    op.execute("COMMIT") 
    
    # 2. Adiciona o valor 'CONSERVA' (maiúsculo, para bater com o que o Python envia)
    op.execute("ALTER TYPE tipo_produto_enum RENAME VALUE 'conserva' TO 'CONSERVA'")


def downgrade() -> None:
    op.execute("COMMIT")
    op.execute("ALTER TYPE tipo_produto_enum RENAME VALUE 'CONSERVA' TO 'conserva'")
