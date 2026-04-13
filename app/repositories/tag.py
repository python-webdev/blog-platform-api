from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    model = Tag

    def __init__(self, db: AsyncSession) -> None:  # pylint: disable=useless-parent-delegation
        super().__init__(db)

    async def get_by_name(self, name: str) -> Tag | None:
        result = await self.db.execute(
            select(Tag).where(Tag.name == name.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str) -> Tag:
        normalised: str = name.lower().strip()
        tag: Tag | None = await self.get_by_name(normalised)
        if tag is None:
            tag = Tag(name=normalised)
            await self.save(tag)
        return tag

    async def get_all(self) -> list[Tag]:
        result = await self.db.execute(select(Tag).order_by(Tag.name.asc()))
        return list(result.scalars().all())
