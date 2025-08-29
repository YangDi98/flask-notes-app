from datetime import datetime, timezone
from sqlalchemy.sql import func
from sqlalchemy import select
from src.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer
from flask_smorest import abort


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @classmethod
    def get_or_404(cls, id):
        stmt = select(cls).where(cls.id == id)
        result = db.session.execute(stmt).scalar_one_or_none()
        if result is None:
            abort(404)
        return result


class CreateUpdateModel(BaseModel):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=datetime.now(timezone.utc),
    )


class SoftDeleteModel(BaseModel):
    __abstract__ = True

    deleted_at: Mapped[datetime] = mapped_column(DateTime)

    def soft_delete(self, commit: bool = False):
        self.deleted_at = datetime.now(timezone.utc)
        if commit:
            db.session.commit()

    @classmethod
    def select_active(cls):
        """Select statement for only non-deleted records"""
        return select(cls).where(cls.deleted_at.is_(None))

    @classmethod
    def select_with_deleted(cls):
        """Select statement for all records including deleted"""
        return select(cls)

    @classmethod
    def select_only_deleted(cls):
        """Select statement for only deleted records"""
        return select(cls).where(cls.deleted_at.isnot(None))

    @classmethod
    def get_active(cls, **filters):
        """Get active records with optional filters"""
        stmt = cls.select_active()
        for attr, value in filters.items():
            if hasattr(cls, attr):
                stmt = stmt.where(getattr(cls, attr) == value)
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def get_by_id(cls, id, include_deleted=False):
        """Get record by ID, excluding deleted by default"""
        if include_deleted:
            stmt = select(cls).where(cls.id == id)
        else:
            stmt = cls.select_active().where(cls.id == id)
        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def get_all(cls, include_deleted=False):
        """Get all records, excluding deleted by default"""
        if include_deleted:
            stmt = cls.select_with_deleted()
        else:
            stmt = cls.select_active()
        return db.session.execute(stmt).scalars().all()

    @classmethod
    def get_or_404(cls, id, include_deleted=False):
        if include_deleted:
            stmt = select(cls).where(cls.id == id)
        else:
            stmt = cls.select_active().where(cls.id == id)

        result = db.session.execute(stmt).scalar_one_or_none()
        if result is None:
            abort(404)
        return result
