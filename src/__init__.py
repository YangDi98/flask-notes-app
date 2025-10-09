from flask import Flask, jsonify
from flask_smorest import Api
from marshmallow.exceptions import ValidationError
from http import HTTPStatus
from datetime import timedelta
from dotenv import load_dotenv
import os

from src.views.notes import note_blueprint
from src.views.categories import category_blueprint
from src.views.auth import auth_blueprint
from src.models.users import User
from .extensions import db, migrate, bcrypt, jwt


def create_app():
    load_dotenv()
    app = Flask("Flask API")
    app.config["API_TITLE"] = "Notes API"
    app.config["API_VERSION"] = "1.0.0"
    app.config["OPENAPI_VERSION"] = "3.0.2"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes_db.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # silence warnings
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from . import models_registry  # noqa: F401

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user.id)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.execute(
            User.select_active().where(
                User.active.is_(True), User.id == identity
            )
        ).scalar_one_or_none()

    @app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
    def handle_unprocessable_entity(err):
        return (
            jsonify(
                {
                    "description": "Input Failed Valiation",
                    "errors": (
                        err.exc.messages.get("json")
                        if hasattr(err, "exc")
                        else "Input Failed Validation"
                    ),
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return (
            jsonify(
                {
                    "description": "Input Failed Validation",
                    "errors": err.messages,
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    api = Api(app)

    api.register_blueprint(note_blueprint)
    api.register_blueprint(category_blueprint)
    api.register_blueprint(auth_blueprint)
    return app
