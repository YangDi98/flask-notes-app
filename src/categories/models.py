from src.models import CreateUpdateModel, SoftDeleteModel
from sqlalchemy import ForeignKey, Integer, String
from src.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_smorest import abort
from typing import TYPE_CHECKING, Optional

from src.users.models import User

if TYPE_CHECKING:
    from src.notes.models import Note


class Category(CreateUpdateModel, SoftDeleteModel):
    __tablename__ = "categories"
    __table_args__ = (db.Index("idx_name", "name"),)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    color: Mapped[str] = mapped_column(
        String(7), nullable=True
    )  # e.g., Hex color code

    user: Mapped["User"] = relationship(back_populates="categories")
    notes: Mapped[list["Note"]] = relationship(back_populates="category")

    @classmethod
    def find_category_by_user_and_id(
        cls, user_id: int, id: int, include_deleted: bool = False
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
    def find_category_by_user_and_id_or_404(
        cls, user_id: int, id: int, include_deleted: bool = False
    ):
        result = cls.find_category_by_user_and_id(
            user_id, id, include_deleted=include_deleted
        )
        if result is None:
            abort(404)
        return result

    @classmethod
    def filter(
        cls,
        user_id: int,
        include_deleted: bool = False,
        name: Optional[str] = None,
    ):
        stmt = (
            cls.select_active()
            if not include_deleted
            else cls.select_with_deleted()
        )
        stmt = stmt.where(cls.user_id == user_id)
        if name:
            stmt = stmt.where(cls.name.ilike(f"%{name}%"))
        return db.session.scalars(stmt.order_by(cls.created_at.desc())).all()
