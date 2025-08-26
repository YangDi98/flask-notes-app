from sqlalchemy import or_, and_
from datetime import datetime
from typing import Optional

from src.extensions import db
from src.models import CreateUpdateModel, SoftDeleteModel


class Note(CreateUpdateModel, SoftDeleteModel):
    __tablename__ = "notes"
    __table_args__ = (db.Index("idx_created_at_id", "created_at", "id"),)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)

    @classmethod
    def find_note_by_id(cls, id):
        return cls.get_by_id(id=id)

    @classmethod
    def filter(
        cls,
        title: Optional[str] = None,
        cursor_created_at: Optional[datetime] = None,
        cursor_id: Optional[int] = None,
        limit: Optional[int] = 100,
    ):
        stmt = cls.select_active()
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
        return db.session.scalars(
            stmt.order_by(Note.created_at.desc(), Note.id.desc()).limit(limit)
        ).all()
