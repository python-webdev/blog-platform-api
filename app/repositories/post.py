import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import Post
from app.models.user import User
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    model = Post

    def __init__(self, db: AsyncSession) -> None:  # pylint: disable=useless-parent-delegation
        super().__init__(db)

    async def get_by_slug(self, slug: str) -> Post | None:
        result = await self.db.execute(
            select(Post)
            .where(Post.slug == slug)
            .options(selectinload(Post.author), selectinload(Post.tags))
        )
        return result.scalar_one_or_none()

    async def get_published_feed(
        self,
        page: int,
        page_size: int,
        tag: str | None = None,
        author_username: str | None = None,
    ) -> tuple[list[Post], int]:
        query: Select[tuple[Post]] = (
            select(Post)
            .where(Post.status == "published")
            .options(selectinload(Post.author), selectinload(Post.tags))
        )

        if tag is not None:
            query = query.where(Post.tags.any(name=tag))

        if author_username is not None:
            query = query.join(Post.author).where(
                User.username == author_username
            )

        count_query = select(func.count()).select_from(query.subquery())  # pylint: disable=not-callable
        total_result = await self.db.execute(count_query)
        total: int = total_result.scalar_one()

        query = (
            query.order_by(Post.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        posts: list[Post] = list(result.scalars().all())

        return posts, total

    async def get_author_posts(
        self,
        author_id: uuid.UUID,
        page: int,
        page_size: int,
        published_only: bool = True,
    ) -> tuple[list[Post], int]:
        query: Select[tuple[Post]] = (
            select(Post)
            .where(Post.author_id == author_id)
            .options(selectinload(Post.tags))
        )

        if published_only:
            query = query.where(Post.status == "published")

        count_query = select(func.count()).select_from(query.subquery())  # pylint: disable=not-callable
        total_result = await self.db.execute(count_query)
        total: int = total_result.scalar_one()

        query = (
            query.order_by(Post.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        posts: list[Post] = list(result.scalars().all())

        return posts, total

    async def slug_exists(self, slug: str) -> bool:
        result = await self.db.execute(
            select(Post.id).where(Post.slug == slug).limit(1)
        )
        return result.scalar_one_or_none() is not None
