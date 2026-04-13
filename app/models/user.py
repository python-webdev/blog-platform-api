from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.post import Post


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
        lazy="noload",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="author",
        lazy="noload",
    )
