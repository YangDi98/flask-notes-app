from sqlalchemy import or_, and_
from datetime import datetime
from typing import Optional

from src.extensions import db
from src.models import CreateUpdateModel, SoftDeleteModel
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.users.models import User


class Note(CreateUpdateModel, SoftDeleteModel):
    __tablename__ = "notes"
    __table_args__ = (db.Index("idx_created_at_id", "created_at", "id"),)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0"
    )

    user: Mapped["User"] = relationship(back_populates="notes")

    @classmethod
    def find_note_by_id(cls, id):
        return cls.get_by_id(id=id)

    @classmethod
    def filter(
        cls,
        user_id: int,
        title: Optional[str] = None,
        cursor_created_at: Optional[datetime] = None,
        cursor_id: Optional[int] = None,
        limit: Optional[int] = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        archived: bool = False,
    ):
        stmt = cls.select_active().where(cls.user_id == user_id)
        if cursor_id and cursor_created_at:
            stmt = stmt.where(
                or_(
                    Note.created_at < cursor_created_at,
                    and_(
                        Note.created_at == cursor_created_at,
                        Note.id < cursor_id,
                    ),
                )
            )
        elif cursor_created_at:
            stmt = stmt.where(Note.created_at < cursor_created_at)
        if title:
            stmt = stmt.where(Note.title.like(f"%{title}%"))
        if start_date:
            stmt = stmt.where(Note.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Note.created_at <= end_date)
        if archived is not None:
            stmt = stmt.where(Note.archived.is_(archived))
        return db.session.scalars(
            stmt.order_by(Note.created_at.desc(), Note.id.desc()).limit(limit)
        ).all()
