"""mesclando heads

Revision ID: 27e04fd604d0
Revises: 748fa6153b85, ccf2b4360cde
Create Date: 2026-09-22 12:42:11.910718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27e04fd604d0'
down_revision: Union[str, Sequence[str], None] = ('748fa6153b85', 'ccf2b4360cde')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
