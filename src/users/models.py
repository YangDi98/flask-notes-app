from src.models import CreateUpdateModel, SoftDeleteModel
from src.extensions import db
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from flask_smorest import abort

if TYPE_CHECKING:
    from src.notes.models import Note
    from src.categories.models import Category


class User(CreateUpdateModel, SoftDeleteModel):
    __tablename__ = "users"
    __table_args__ = (db.Index("email_idx", "email"),)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )

    notes: Mapped[list["Note"]] = relationship(back_populates="user")
    categories: Mapped[list["Category"]] = relationship(back_populates="user")

    @classmethod
    def get_by_id(
        cls, id, include_deleted: bool = False, include_inactive: bool = False
    ):
        stmt = (
            cls.select_with_deleted()
            if include_deleted
            else cls.select_active()
        )
        if not include_inactive:
            stmt = stmt.where(cls.active.is_(True))
        stmt = stmt.where(cls.id == id)
        result = db.session.execute(stmt).scalar_one_or_none()
        return result

    @classmethod
    def get_or_404(
        cls, id, include_deleted: bool = False, include_inactive: bool = False
    ):
        result = cls.get_by_id(
            id,
            include_deleted=include_deleted,
            include_inactive=include_inactive,
        )
        if result is None:
            abort(404)
        return result
