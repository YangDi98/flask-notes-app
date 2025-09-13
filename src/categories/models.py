from src.models import CreateUpdateModel, SoftDeleteModel
from sqlalchemy import ForeignKey, Integer, String
from src.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.users.models import User
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
