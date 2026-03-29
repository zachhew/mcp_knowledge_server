from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums.audit_action import AuditAction
from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    client_id: Mapped[str | None] = mapped_column(ForeignKey("api_clients.id", ondelete="SET NULL"), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    action_type: Mapped[AuditAction] = mapped_column(String(50), nullable=False)
    input_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_status: Mapped[str] = mapped_column(String(50), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)