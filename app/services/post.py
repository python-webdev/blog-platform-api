import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolationError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.slugify import generate_unique_slug
from app.models.post import Post
from app.repositories.post import PostRepository
from app.repositories.tag import TagRepository


@dataclass
class CreatePostInput:
    title: str
    body: str
    tags: list[str]


@dataclass
class UpdatePostInput:
    title: str | None = None
    body: str | None = None
    tags: list[str] | None = None


@dataclass
class PaginatedPosts:
    posts: list[Post]
    total: int
    page: int
    page_size: int
    total_pages: int


class PostService:
    def __init__(
        self,
        post_repository: PostRepository,
        tag_repository: TagRepository,
        db_session: AsyncSession,
    ) -> None:
        self.post_repository = post_repository
        self.tag_repository = tag_repository
        self.db_session = db_session

    async def create_post(
        self,
        author_id: uuid.UUID,
        data: CreatePostInput,
    ) -> Post:
        slug: str = await generate_unique_slug(
            title=data.title,
            db=self.db_session,
        )
        tags = [
            await self.tag_repository.get_or_create(name=tag_name)
            for tag_name in data.tags
        ]

        post = Post(
            author_id=author_id,
            title=data.title,
            body=data.body,
            slug=slug,
            status="draft",
            tags=tags,
        )
        return await self.post_repository.save(post)

    async def get_by_slug(self, slug: str) -> Post:
        post: Post | None = await self.post_repository.get_by_slug(slug)
        if post is None:
            raise NotFoundError("Post", slug)
        return post

    async def get_feed(
        self,
        page: int,
        page_size: int,
        tag: str | None = None,
        author_username: str | None = None,
    ) -> PaginatedPosts:
        posts, total = await self.post_repository.get_published_feed(
            page=page,
            page_size=page_size,
            tag=tag,
            author_username=author_username,
        )
        return PaginatedPosts(
            posts=posts,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=-(-total // page_size),  # Ceiling division
        )

    async def update_post(
        self,
        slug: str,
        requester_id: uuid.UUID,
        data: UpdatePostInput,
    ) -> Post:
        post: Post = await self.get_by_slug(slug)

        if post.author_id != requester_id:
            raise PermissionDeniedError("Only the author can update this post")

        if data.title is not None:
            post.title = data.title
            post.slug = await generate_unique_slug(
                title=data.title,
                db=self.db_session,
            )

        if data.body is not None:
            post.body = data.body

        if data.tags is not None:
            post.tags = [
                await self.tag_repository.get_or_create(name=tag_name)
                for tag_name in data.tags
            ]

        return await self.post_repository.save(post)

    async def publish_post(
        self,
        slug: str,
        requester_id: uuid.UUID,
    ) -> Post:
        post: Post = await self.get_by_slug(slug)

        if post.author_id != requester_id:
            raise PermissionDeniedError(
                "Only the author can publish this post"
            )

        if post.status == "archived":
            raise BusinessRuleViolationError(
                "Archived posts cannot be published"
            )

        if post.status == "published":
            raise BusinessRuleViolationError("Post is already published")

        if not post.title.strip() or not post.body.strip():
            raise BusinessRuleViolationError(
                "Post must have a title and body to be published"
            )

        post.status = "published"
        post.published_at = datetime.now(timezone.utc)
        return await self.post_repository.save(post)

    async def unpublish_post(
        self,
        slug: str,
        requester_id: uuid.UUID,
    ) -> Post:
        post: Post = await self.get_by_slug(slug)

        if post.author_id != requester_id:
            raise PermissionDeniedError(
                "Only the author can unpublish this post"
            )

        if post.status != "published":
            raise BusinessRuleViolationError(
                "Only published posts can be unpublished"
            )

        post.status = "draft"
        post.published_at = None
        return await self.post_repository.save(post)

    async def archive_post(
        self,
        slug: str,
        requester_id: uuid.UUID,
    ) -> Post:
        post: Post = await self.get_by_slug(slug)

        if post.author_id != requester_id:
            raise PermissionDeniedError(
                "Only the author can archive this post"
            )

        if post.status == "archived":
            raise BusinessRuleViolationError("Post is already archived")

        post.status = "archived"
        return await self.post_repository.save(post)

    async def delete_post(
        self,
        slug: str,
        requester_id: uuid.UUID,
        requester_is_admin: bool = False,
    ) -> None:
        post: Post = await self.get_by_slug(slug)

        if post.author_id != requester_id and not requester_is_admin:
            raise PermissionDeniedError(
                "Only the author or an admin can delete this post"
            )

        await self.post_repository.delete(post)

    async def get_author_posts(
        self,
        author_id: uuid.UUID,
        page: int,
        page_size: int,
        published_only: bool = True,
    ) -> PaginatedPosts:
        posts, total = await self.post_repository.get_author_posts(
            author_id=author_id,
            page=page,
            page_size=page_size,
            published_only=published_only,
        )
        return PaginatedPosts(
            posts=posts,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=-(-total // page_size),  # Ceiling division
        )
