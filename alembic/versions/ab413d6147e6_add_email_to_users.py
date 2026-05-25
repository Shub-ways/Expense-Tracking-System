"""add_email_to_users

Revision ID: ab413d6147e6
Revises: 23ea90e2b9ec
Create Date: 2026-05-26 01:42:26.964832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab413d6147e6'
down_revision: Union[str, None] = '23ea90e2b9ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.exc import ProgrammingError
    
    # Try adding the column, ignore if it already exists
    try:
        op.add_column('users', sa.Column('email', sa.String(length=120), nullable=True))
    except ProgrammingError as e:
        if "Duplicate column name" not in str(e) and "1060" not in str(e):
            raise
    except Exception as e:
        if "Duplicate column" not in str(e):
            raise

    # Try adding the unique constraint, ignore if it already exists
    try:
        op.create_unique_constraint('uq_users_email', 'users', ['email'])
    except ProgrammingError as e:
        pass
    except Exception as e:
        pass


def downgrade() -> None:
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'email')
