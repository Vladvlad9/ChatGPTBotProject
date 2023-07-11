"""create db

Revision ID: 7cd0ca4f4239
Revises: 
Create Date: 2023-07-05 12:55:55.592440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cd0ca4f4239'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('subscriptions',
                    sa.Column('id', sa.SmallInteger(), nullable=False),
                    sa.Column('name', sa.Text(), nullable=False),
                    sa.Column('price', sa.Text(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )

    # op.create_table('referrals',
    #                 sa.Column('id', sa.SmallInteger(), nullable=False),
    #                 sa.Column('user_id', sa.BigInteger(), nullable=False),
    #                 sa.Column('referral_id', sa.BigInteger(), nullable=False),
    #                 sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='NO ACTION'),
    #                 sa.PrimaryKeyConstraint('id')
    #                 )

    op.create_table('users',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('user_id', sa.BigInteger(), nullable=False),
                    sa.Column('queries_chat_gpt', sa.Integer()),
                    sa.Column('queries_img', sa.Integer()),
                    sa.Column('subscription_id', sa.Integer()),
                    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='NO ACTION'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('subscriptions')
    op.drop_table('users')
