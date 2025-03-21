from __future__ import annotations
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from kupala.contrib.sqlalchemy.models import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    password: Mapped[str] = mapped_column(default="")
    profile: Mapped[Profile] = relationship("Profile", back_populates="user")

    @property
    def identity(self) -> str:
        return self.name


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    bio: Mapped[str]
    user: Mapped[User] = relationship("User", back_populates="profile")
