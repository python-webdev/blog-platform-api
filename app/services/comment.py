import uuid
from dataclasses import dataclass

from app.core.exceptions import (
    BusinessRuleViolationError,
    NotFoundError,
    PermissionDeniedError,
)
from app.models.comment import Comment
from app.repositories.comment import CommentRepository
from app.repositories.post import PostRepository


@dataclass
class CreateCommentInput:
    body: str
    parent_id: uuid.UUID | None = None


@dataclass
class PaginatedComments:
    comments: list[Comment]
    total: int
    page: int
    page_size: int
    total_pages: int


class CommentService:
    def __init__(
        self,
        comment_repository: CommentRepository,
        post_repository: PostRepository,
    ) -> None:
        self.comment_repository = comment_repository
        self.post_repository = post_repository

    async def create_comment(
        self,
        post_slug: str,
        author_id: uuid.UUID,
        data: CreateCommentInput,
    ) -> Comment:
        # Ensure the post exists
        post = await self.post_repository.get_by_slug(post_slug)
        if post is None:
            raise NotFoundError("Post", post_slug)

        if post.status != "published":
            raise BusinessRuleViolationError(
                "Comments are only allowed on published posts"
            )

        if data.parent_id is not None:
            parent: Comment | None = await self.comment_repository.get_by_id(
                data.parent_id
            )
            if parent is None:
                raise NotFoundError("Comment", str(data.parent_id))
            if parent.post_id != post.id:
                raise BusinessRuleViolationError(
                    "Parent comment does not belong to the same post"
                )
            if parent.parent_id is not None:
                raise BusinessRuleViolationError(
                    "Replies to replies are not allowed"
                )

        comment = Comment(
            post_id=post.id,
            author_id=author_id,
            body=data.body,
            parent_id=data.parent_id,
        )
        return await self.comment_repository.save(comment)

    async def get_post_comments(
        self,
        post_slug: str,
        page: int,
        page_size: int,
    ) -> PaginatedComments:
        post = await self.post_repository.get_by_slug(post_slug)
        if post is None:
            raise NotFoundError("Post", post_slug)

        comments, total = await self.comment_repository.get_post_comments(
            post_id=post.id,
            page=page,
            page_size=page_size,
        )
        return PaginatedComments(
            comments=comments,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=-(-total // page_size),  # Ceiling division
        )

    async def delete_comment(
        self,
        comment_id: uuid.UUID,
        requester_id: uuid.UUID,
        requester_is_admin: bool = False,
    ) -> None:
        comment: Comment | None = await self.comment_repository.get_by_id(
            comment_id
        )
        if comment is None:
            raise NotFoundError("Comment", str(comment_id))

        if comment.author_id != requester_id and not requester_is_admin:
            raise PermissionDeniedError(
                "Only the author or an admin can delete this comment"
            )

        await self.comment_repository.delete(comment)
