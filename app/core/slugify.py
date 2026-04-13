import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post


def _build_base_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug


async def _slug_exists(slug: str, db: AsyncSession) -> bool:
    result = await db.execute(select(Post).where(Post.slug == slug).limit(1))
    return result.scalar_one_or_none() is not None


async def generate_unique_slug(title: str, db: AsyncSession) -> str:
    base_slug = _build_base_slug(title)
    slug = base_slug

    while await _slug_exists(slug, db):
        suffix: str = uuid.uuid4().hex[:4]
        slug = f"{base_slug}-{suffix}"

    return slug
