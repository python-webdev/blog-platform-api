import uuid
from dataclasses import dataclass

import bcrypt

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.models.user import User
from app.repositories.user import UserRepository


@dataclass
class RegisterUserInput:
    username: str
    email: str
    password: str


@dataclass
class UpdateUserInput:
    bio: str | None = None


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register(self, data: RegisterUserInput) -> User:
        if await self.user_repository.email_exists(data.email):
            raise ConflictError("Email already in use")

        if await self.user_repository.username_exists(data.username):
            raise ConflictError("Username already in use")

        hashed_password: str = bcrypt.hashpw(
            data.password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hashed_password,
        )
        return await self.user_repository.save(user)

    async def get_by_username(self, username: str) -> User:
        user: User | None = await self.user_repository.get_by_username(
            username
        )
        if user is None:
            raise NotFoundError("User", username)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user: User | None = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", str(user_id))
        return user

    async def update(
        self,
        user_id: uuid.UUID,
        requester_id: uuid.UUID,
        data: UpdateUserInput,
    ) -> User:
        user: User = await self.get_by_id(user_id)
        if user.id != requester_id:
            raise PermissionDeniedError("You can only update your own profile")
        if data.bio is not None:
            user.bio = data.bio
        return await self.user_repository.save(user)

    async def deactivate(
        self, user_id: uuid.UUID, requester_id: uuid.UUID
    ) -> None:
        user: User = await self.get_by_id(user_id)
        if user.id != requester_id:
            raise PermissionDeniedError(
                "You can only deactivate your own account"
            )
        user.is_active = False
        await self.user_repository.save(user)

    async def verify_password(self, email: str, password: str) -> User:
        user: User | None = await self.user_repository.get_by_email(email)

        if user is None or not bcrypt.checkpw(
            password.encode("utf-8"),
            (user.password_hash if user else "").encode("utf-8"),
        ):
            raise PermissionDeniedError("Invalid credentials")

        if not user.is_active:
            raise PermissionDeniedError("Account is deactivated")

        return user
