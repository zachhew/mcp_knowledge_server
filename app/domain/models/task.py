from sqlalchemy import ForeignKey, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.task_priority import TaskPriority
from app.domain.enums.task_status import TaskStatus
from app.infrastructure.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Task(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tasks"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        )
    )

    priority: Mapped[TaskPriority] = mapped_column(
        Enum(
            TaskPriority,
            name="task_priority_enum",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        )
    )
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    project = relationship("Project", back_populates="tasks")