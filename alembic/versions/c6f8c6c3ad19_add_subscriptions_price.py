"""add subscriptions price

Revision ID: c6f8c6c3ad19
Revises: 818f84421d02
Create Date: 2023-07-05 15:37:33.296100

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from models import create_sync_session, Subscription
from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError

revision = 'c6f8c6c3ad19'
down_revision = '818f84421d02'
branch_labels = None
depends_on = None

prices = [
    'Бесплатно',
    '79,00 ₽',
    '299,00 ₽',
    '699,00 ₽',
    '1699,00 ₽',
    '99,00 ₽',
    '189,00 ₽',
    '349,00 ₽'
]


@create_sync_session
def upgrade(session: Session = None) -> None:
    for price in prices:
        price = Subscription(price=price)
        session.add(price)
        try:
            session.commit()
        except IntegrityError:
            pass


@create_sync_session
def downgrade(session: Session = None) -> None:
    for price in prices:
        session.execute(
            sa.delete(Subscription)
                .where(Subscription.price == price)
        )
        session.commit()
