"""add subscriptions

Revision ID: 818f84421d02
Revises: 7cd0ca4f4239
Create Date: 2023-07-05 13:54:19.968083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from models import create_sync_session, Subscription
from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError

revision = '818f84421d02'
down_revision = '7cd0ca4f4239'
branch_labels = None
depends_on = None

subscriptions = ['Стандарт',
                 '📅 1 день',
                 '📅 7 дней',
                 '📅 30 дней',
                 '📅 90 дней',
                 '🔢 20 запросов',
                 '🔢 50 запросов',
                 '🔢 100 запросов']


@create_sync_session
def upgrade(session: Session = None) -> None:
    for subscription in subscriptions:
        subscription = Subscription(name=subscription, price=0)
        session.add(subscription)
        try:
            session.commit()
        except IntegrityError:
            pass


@create_sync_session
def downgrade(session: Session = None) -> None:
    for subscription in subscriptions:
        session.execute(
            sa.delete(Subscription)
            .where(Subscription.name == subscription)
        )
        session.commit()
