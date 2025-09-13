from sqlalchemy import or_, and_
from flask_smorest import abort
from datetime import datetime
from typing import Optional

from src.extensions import db
from src.models import CreateUpdateModel, SoftDeleteModel
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.users.models import User

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.categories.models import Category


class Note(CreateUpdateModel, SoftDeleteModel):
    __tablename__ = "notes"
    __table_args__ = (db.Index("idx_created_at_id", "created_at", "id"),)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0"
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("categories.id", name="fk_notes_category_id"),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="notes")
    category: Mapped[Optional["Category"]] = relationship(
        back_populates="notes"
    )

    @classmethod
    def find_note_by_user_and_id(
        cls, user_id, id, include_deleted: bool = False
    ):
        user = User.get_by_id(user_id)
        if user is None:
            return None
        stmt = (
            cls.select_with_deleted()
            if include_deleted
            else cls.select_active()
        )
        stmt = stmt.where(cls.user_id == user_id, cls.id == id)
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def find_note_by_user_and_id_or_404(
        cls, user_id, id, include_deleted: bool = False
    ):
        User.get_or_404(user_id)
        stmt = (
            cls.select_with_deleted()
            if include_deleted
            else cls.select_active()
        )
        stmt = stmt.where(cls.user_id == user_id, cls.id == id)
        result = db.session.execute(stmt).scalar_one_or_none()
        if result is None:
            abort(404)
        return result

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
        category_id: Optional[int] = None,
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
        if category_id is not None:
            stmt = stmt.where(Note.category_id == category_id)
        return db.session.scalars(
            stmt.order_by(Note.created_at.desc(), Note.id.desc()).limit(limit)
        ).all()

    def restore(self, commit: bool = False):
        self.deleted_at = None
        if commit:
            db.session.commit()
        return self
