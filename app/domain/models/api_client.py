from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ApiClient(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "api_clients"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_api_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    scopes: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)