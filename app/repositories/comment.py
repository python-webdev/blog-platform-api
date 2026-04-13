import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    model = Comment

    def __init__(self, db: AsyncSession) -> None:  # pylint: disable=useless-parent-delegation
        super().__init__(db)

    async def get_post_comments(
        self, post_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[Comment], int]:
        query = (
            select(Comment)
            .where(
                Comment.post_id == post_id,
                Comment.parent_id.is_(None),
            )
            .options(
                selectinload(Comment.author),
                selectinload(Comment.replies).selectinload(Comment.author),
            )
        )
        count_query = select(func.count()).select_from(query.subquery())  # pylint: disable=not-callable
        total_result = await self.db.execute(count_query)
        total: int = total_result.scalar_one()

        query = (
            query.order_by(Comment.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        comments: list[Comment] = list(result.scalars().all())

        return comments, total
