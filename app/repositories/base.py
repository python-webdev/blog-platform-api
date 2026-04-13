import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, model_id: uuid.UUID) -> ModelT | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == model_id)
        )
        return result.scalar_one_or_none()

    async def save(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.db.delete(instance)
        await self.db.commit()
