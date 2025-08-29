from src.models import CreateUpdateModel, SoftDeleteModel
from src.extensions import db
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.notes.models import Note


class User(CreateUpdateModel, SoftDeleteModel):
    __tablename__ = "users"
    __table_args__ = (db.Index("email_idx", "email"),)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )

    notes: Mapped[list["Note"]] = relationship("Note", back_populates="user")

    @classmethod
    def find_user_by_id(cls, id):
        return cls.get_by_id(id=id)
