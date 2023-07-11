"""create referrals

Revision ID: 3cb57eff8e05
Revises: c6f8c6c3ad19
Create Date: 2023-07-11 11:09:35.003862

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3cb57eff8e05'
down_revision = 'c6f8c6c3ad19'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('referrals',
                    sa.Column('id', sa.SmallInteger(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('referral_id', sa.BigInteger(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='NO ACTION'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('referrals')
