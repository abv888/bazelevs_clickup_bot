from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def orm_add_user(session: AsyncSession, user: User):
    session.add(user)
    await session.commit()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.telegram_id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_all_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()
