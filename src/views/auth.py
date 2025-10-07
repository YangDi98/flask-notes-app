from flask_smorest import Blueprint, abort
from sqlalchemy import select
from http import HTTPStatus

from src.schemas.auth import RegisterSchema, UserSchema
from src.extensions import db, bcrypt
from src.models.users import User

auth_blueprint = Blueprint("auth", __name__, url_prefix="/")


@auth_blueprint.route("/register", methods=["POST"])
@auth_blueprint.arguments(RegisterSchema, location="json")
@auth_blueprint.response(201, UserSchema)
def register(req_json):
    existing_user = db.session.execute(
        select(User).where(User.email == req_json["email"])
    ).scalar_one_or_none()
    if existing_user:
        abort(HTTPStatus.CONFLICT, message="email already exists")

    hashed = bcrypt.generate_password_hash(req_json["password"]).decode(
        "utf-8"
    )
    user = User.create({**req_json, "password": hashed}, commit=False)
    db.session.add(user)
    db.session.commit()
    return user, HTTPStatus.CREATED
