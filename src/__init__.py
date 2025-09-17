from flask import Flask, jsonify
from flask_smorest import Api
from marshmallow.exceptions import ValidationError
from http import HTTPStatus

from src.notes import note_blueprint
from src.categories import category_blueprint
from .extensions import db, migrate


def create_app():
    app = Flask("Flask API")
    app.config["API_TITLE"] = "Notes API"
    app.config["API_VERSION"] = "1.0.0"
    app.config["OPENAPI_VERSION"] = "3.0.2"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes_db.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # silence warnings

    db.init_app(app)
    migrate.init_app(app, db)  # bind db to this app

    from . import models_registry  # noqa: F401

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
    return app
