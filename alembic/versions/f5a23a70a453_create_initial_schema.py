"""create_initial_schema

Revision ID: f5a23a70a453
Revises: 
Create Date: 2026-05-25 00:46:03.988326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a23a70a453'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── Users Table ───────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

    # ─── Expenses Table ────────────────────────────────────────
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.CheckConstraint('amount > 0', name='check_expense_amount_positive'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_expense_date', 'expenses', ['user_id', 'expense_date'], unique=False)
    op.create_index('idx_user_category', 'expenses', ['user_id', 'category'], unique=False)

    # ─── Budgets Table ─────────────────────────────────────────
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('monthly_limit', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.CheckConstraint('monthly_limit > 0', name='check_budget_limit_positive'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'category', name='idx_user_category')
    )

    # ─── Seed Data ─────────────────────────────────────────────
    # Seed default user
    users_table = sa.table(
        'users',
        sa.column('id', sa.Integer),
        sa.column('username', sa.String),
        sa.column('password_hash', sa.String)
    )
    op.bulk_insert(
        users_table,
        [
            {
                'id': 1,
                'username': 'demo',
                'password_hash': '$2b$12$.5fsYsD5E659JmYOItlfQ.5oNZeOLgqxcM8sgxnkWGQpCnd12eqKS'
            }
        ]
    )

    # Seed demo budgets
    budgets_table = sa.table(
        'budgets',
        sa.column('user_id', sa.Integer),
        sa.column('category', sa.String),
        sa.column('monthly_limit', sa.Numeric)
    )
    op.bulk_insert(
        budgets_table,
        [
            {'user_id': 1, 'category': 'Food', 'monthly_limit': 3000.00},
            {'user_id': 1, 'category': 'Rent', 'monthly_limit': 10000.00},
            {'user_id': 1, 'category': 'Shopping', 'monthly_limit': 2000.00},
            {'user_id': 1, 'category': 'Entertainment', 'monthly_limit': 1000.00},
            {'user_id': 1, 'category': 'Other', 'monthly_limit': 500.00},
        ]
    )


def downgrade() -> None:
    op.drop_table('budgets')
    op.drop_table('expenses')
    op.drop_table('users')
