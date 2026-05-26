"""remove_email_from_users

Revision ID: d6d1e524e6a4
Revises: ab413d6147e6
Create Date: 2026-05-26 12:45:32.895740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6d1e524e6a4'
down_revision: Union[str, None] = 'ab413d6147e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.exc import ProgrammingError

    # Drop constraint if exists
    try:
        op.drop_constraint('uq_users_email', 'users', type_='unique')
    except ProgrammingError:
        pass
    except Exception:
        pass

    # Drop column if exists
    try:
        op.drop_column('users', 'email')
    except ProgrammingError:
        pass
    except Exception:
        pass


def downgrade() -> None:
    from sqlalchemy.exc import ProgrammingError

    try:
        op.add_column('users', sa.Column('email', sa.String(length=120), nullable=True))
    except Exception:
        pass

    try:
        op.create_unique_constraint('uq_users_email', 'users', ['email'])
    except Exception:
        pass
