from flask_jwt_extended import current_user
from flask_smorest import abort
from http import HTTPStatus


def user_access_required(func):
    def wrapper(*args, **kwargs):
        if not current_user:
            abort(HTTPStatus.UNAUTHORIZED, message="Missing or invalid token")
        if current_user.id != kwargs.get("user_id"):
            abort(HTTPStatus.FORBIDDEN, message="Access forbidden")
        return func(*args, **kwargs)

    return wrapper
