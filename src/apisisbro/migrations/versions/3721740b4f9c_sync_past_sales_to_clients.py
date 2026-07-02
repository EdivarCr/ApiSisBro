"""sync_past_sales_to_clients

Revision ID: 3721740b4f9c
Revises: 77181f7dcd15
Create Date: 2026-06-26 18:49:21.611720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3721740b4f9c'
down_revision: Union[str, Sequence[str], None] = '77181f7dcd15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Recalcula o passado de todos os clientes baseados na tabela de vendas"""
    op.execute("""
        UPDATE cliente c
        SET 
            total_compras = COALESCE((SELECT SUM(valor_total) FROM vendas v WHERE v.cliente_id = c.id), 0),
            quantidade_compras = (SELECT COUNT(*) FROM vendas v WHERE v.cliente_id = c.id),
            ultima_compra = (SELECT MAX(data_venda) FROM vendas v WHERE v.cliente_id = c.id);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
