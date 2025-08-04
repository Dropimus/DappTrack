"""Switch back to submission_id in airdrop_steps

Revision ID: 9b077a44c4ed
Revises: 95d49604810e
Create Date: 2025-08-04 12:54:45.418234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b077a44c4ed'
down_revision: Union[str, None] = '95d49604810e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
