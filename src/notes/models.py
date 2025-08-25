from src.extensions import db
from sqlalchemy import select, or_, and_
from datetime import datetime, timezone
from typing import Optional


class Note(db.Model):
    __tablename__ = "notes"
    __table_args__ = (db.Index("idx_created_at_id", "created_at", "id"),)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    deleted_at = db.Column(db.DateTime)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    @classmethod
    def find_note_by_id(cls, id):
        return (
            db.session.execute(
                select(Note).where(Note.id == id, Note.deleted_at.is_(None))
            )
            .scalars()
            .first()
        )

    @classmethod
    def filter(
        cls,
        title: Optional[str] = None,
        cursor_created_at: Optional[datetime] = None,
        cursor_id: Optional[int] = None,
        limit: Optional[int] = 100,
    ):
        stmt = select(Note).where(Note.deleted_at.is_(None))
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

    def soft_delete(self, commit: bool = False):
        self.deleted_at = datetime.now(timezone.utc)
        if commit:
            db.session.commit()
