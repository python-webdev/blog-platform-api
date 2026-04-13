import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.tag import Tag
    from app.models.user import User


class Post(BaseModel):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="check_posts_status",
        ),
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(350),
        unique=True,
        nullable=False,
        index=True,
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    author: Mapped["User"] = relationship(
        "User",
        back_populates="posts",
        lazy="noload",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        lazy="noload",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="post_tags",
        back_populates="posts",
        lazy="noload",
    )
