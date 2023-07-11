from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from schemas import SubscriptionInDBSchema
from models import Subscription, create_async_session, create_sync_session


class CRUDSubscription(object):

    @staticmethod
    @create_async_session
    async def get(subscription_id: int, session: AsyncSession = None) -> SubscriptionInDBSchema | None:
        subscriptions = await session.execute(
            select(Subscription)
            .where(Subscription.id == subscription_id)
        )
        if subscription := subscriptions.first():
            return SubscriptionInDBSchema(**subscription[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[SubscriptionInDBSchema]:
        subscriptions = await session.execute(
            select(Subscription)
        )
        return [SubscriptionInDBSchema(**subscription[0].__dict__) for subscription in subscriptions]

