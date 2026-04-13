import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


class Comment(BaseModel):
    __tablename__ = "comments"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="comments",
        lazy="noload",
    )
    author: Mapped["User"] = relationship(
        "User",
        back_populates="comments",
        lazy="noload",
    )
    parent: Mapped["Comment | None"] = relationship(
        "Comment",
        back_populates="replies",
        foreign_keys="[Comment.parent_id]",
        remote_side="Comment.id",
        lazy="noload",
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        foreign_keys="[Comment.parent_id]",
        lazy="noload",
    )
