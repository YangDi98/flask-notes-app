from datetime import datetime, timezone
from sqlalchemy.sql import func
from sqlalchemy import select
from src.extensions import db


class CreateUpdateModel(db.Model):
    __abstract__ = True

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=datetime.now(timezone.utc),
    )


class SoftDeleteModel(db.Model):
    __abstract__ = True

    deleted_at = db.Column(db.DateTime)

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
