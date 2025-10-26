from flask import jsonify, request
from flask_smorest import Blueprint, abort
from sqlalchemy import select
from http import HTTPStatus
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_refresh_cookies,
    jwt_required,
    current_user,
    unset_jwt_cookies,
)

from src.schemas.auth import RegisterSchema, UserSchema, UpdatePasswordSchema
from src.extensions import db, bcrypt
from src.models.users import User

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@auth_blueprint.route("/register", methods=["POST"])
@auth_blueprint.arguments(RegisterSchema, location="json")
@auth_blueprint.response(201, UserSchema)
def register(req_json):
    existing_user = db.session.execute(
        select(User).where(User.email == req_json["email"])
    ).scalar_one_or_none()
    if existing_user:
        abort(HTTPStatus.CONFLICT, message="Email already registered")

    hashed = bcrypt.generate_password_hash(req_json["password"]).decode(
        "utf-8"
    )
    user = User.create({**req_json, "password": hashed}, commit=False)
    db.session.add(user)
    db.session.commit()
    return user, HTTPStatus.CREATED


@auth_blueprint.route("/update_password", methods=["POST"])
@auth_blueprint.arguments(UpdatePasswordSchema, location="json")
@auth_blueprint.response(200, UserSchema)
@jwt_required()
def update_password(req_json):
    user = current_user
    if not bcrypt.check_password_hash(user.password, req_json["password"]):
        abort(HTTPStatus.UNAUTHORIZED, message="Invalid current password")
    user.set_password(req_json["new_password"])
    return user, HTTPStatus.OK


@auth_blueprint.route("/login", methods=["POST"])
def login():
    req_json = request.get_json()
    stmt = User.select_active().where(
        User.email == req_json["email"].lower(), User.active.is_(True)
    )
    user = db.session.execute(stmt).scalar_one_or_none()
    if not user or not bcrypt.check_password_hash(
        user.password, req_json["password"]
    ):
        abort(HTTPStatus.UNAUTHORIZED, message="Invalid email or password")
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    response = jsonify({"access_token": access_token})
    set_refresh_cookies(response, refresh_token)
    return response, HTTPStatus.OK


@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": access_token}), HTTPStatus.OK


@auth_blueprint.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    current_user.update({"last_logout_at": db.func.now()}, commit=True)
    response = jsonify({"message": "logout successful"})
    unset_jwt_cookies(response)
    return response, HTTPStatus.OK


@auth_blueprint.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    return (
        jsonify(
            {
                "logged_in_as": f"{current_user.first_name} "
                f"{current_user.last_name}"
            }
        ),
        200,
    )
