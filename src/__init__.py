from flask import Flask, jsonify, request
from flask_smorest import Api
from flask_jwt_extended import current_user
from flask_babel import gettext
from marshmallow.exceptions import ValidationError
from http import HTTPStatus
from datetime import timedelta, datetime, timezone
import os

from src.views.notes import note_blueprint
from src.views.categories import category_blueprint
from src.views.auth import auth_blueprint
from src.models.users import User
from .extensions import db, migrate, bcrypt, jwt, cors, babel


def error_response(status, error, message, details=None):
    response = jsonify(
        {
            "status": status,
            "error": error,
            "message": message,
            "details": details,
        }
    )
    response.status_code = status
    return response


def register_error_handlers(app):
    @app.errorhandler(HTTPStatus.FORBIDDEN)
    def handle_forbidden(e):
        return error_response(
            HTTPStatus.FORBIDDEN,
            gettext("Forbidden"),
            gettext("You do not have permission to access this resource."),
        )

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def handle_not_found(e):
        return error_response(
            HTTPStatus.NOT_FOUND,
            gettext("Not Found"),
            gettext("The requested resource was not found."),
        )

    @app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
    def handle_unprocessable_entity(err):
        return error_response(
            HTTPStatus.BAD_REQUEST,
            gettext("Bad Request"),
            gettext("Input Failed Validation"),
            err.exc.messages if hasattr(err, "exc") else None,
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return error_response(
            HTTPStatus.BAD_REQUEST,
            gettext("Bad Request"),
            gettext("Input Failed Validation"),
            err.messages,
        )


def register_jwt_handlers(jwt_manager):
    @jwt_manager.user_identity_loader
    def user_identity_lookup(user):
        return str(user.id)

    @jwt_manager.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.execute(
            User.select_active().where(
                User.active.is_(True), User.id == int(identity)
            )
        ).scalar_one_or_none()

    @jwt_manager.user_lookup_error_loader
    def user_lookup_error_callback(jwt_header, jwt_data):
        return error_response(
            HTTPStatus.UNAUTHORIZED,
            gettext("Unauthorized"),
            gettext("User not found or inactive."),
        )

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        user = db.session.execute(
            User.select_with_deleted().where(
                User.id == int(jwt_payload["sub"])
            )
        ).scalar_one_or_none()
        if user is None or user.deleted_at is not None or not user.active:
            return True
        last_logout = user.last_logout_at
        if last_logout is None:
            return False
        token_iat = datetime.fromtimestamp(jwt_payload["iat"], tz=timezone.utc)
        return token_iat <= last_logout.replace(tzinfo=timezone.utc)

    @jwt_manager.unauthorized_loader
    def jwt_missing(callback):
        return error_response(
            HTTPStatus.UNAUTHORIZED,
            gettext("Unauthorized"),
            gettext("Missing or invalid authentication token."),
        )

    @jwt_manager.invalid_token_loader
    def jwt_invalid(callback):
        return error_response(
            HTTPStatus.UNAUTHORIZED,
            gettext("Unauthorized"),
            gettext("Token is invalid or expired."),
        )

    @jwt_manager.expired_token_loader
    def jwt_expired(jwt_header, jwt_payload):
        return error_response(
            HTTPStatus.UNAUTHORIZED,
            gettext("Unauthorized"),
            gettext("Token has expired."),
        )

    @jwt_manager.revoked_token_loader
    def jwt_revoked(jwt_header, jwt_payload):
        return error_response(
            HTTPStatus.UNAUTHORIZED,
            gettext("Unauthorized"),
            gettext("Token has been revoked."),
        )


def get_locale():
    try:
        user = current_user
        if user and user.preferred_language:
            print(f"Using user preferred language: {user.preferred_language}")
            return user.preferred_language
    except RuntimeError:
        # current_user is not available (no valid JWT token)
        pass
    # Fallback to browser's preferred language or default to 'en'
    if hasattr(request, "accept_languages") and request.accept_languages:
        accept_langs = request.accept_languages
        selected = accept_langs.best_match(["en_CA", "zh_CN"]) or "en_CA"
        return selected
    return "en_CA"


def create_app(test_config=None):
    app = Flask("Flask API")
    app.config["API_TITLE"] = "Notes API"
    app.config["API_VERSION"] = "1.0.0"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///notes_db.sqlite"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # silence warnings
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/auth/refresh"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True

    # CORS Configuration
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    app.config["CORS_ORIGINS"] = [frontend_url]
    app.config["CORS_ALLOW_HEADERS"] = [
        "Content-Type",
        "Authorization",
        "X-CSRF-TOKEN",
    ]
    app.config["CORS_METHODS"] = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
    ]
    app.config["CORS_SUPPORTS_CREDENTIALS"] = True

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        origins=app.config["CORS_ORIGINS"],
        allow_headers=app.config["CORS_ALLOW_HEADERS"],
        methods=app.config["CORS_METHODS"],
        supports_credentials=app.config["CORS_SUPPORTS_CREDENTIALS"],
    )
    babel.init_app(app, locale_selector=get_locale)

    from . import models_registry  # noqa: F401

    register_error_handlers(app)
    register_jwt_handlers(jwt)

    api = Api(app)

    api.register_blueprint(note_blueprint)
    api.register_blueprint(category_blueprint)
    api.register_blueprint(auth_blueprint)
    return app
