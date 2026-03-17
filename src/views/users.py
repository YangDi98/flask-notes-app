from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, current_user
from http import HTTPStatus
from src.views.utils import user_access_required
from src.schemas.users import UpdateUserSchema, UserSchema

user_blueprint = Blueprint("user", __name__, url_prefix="/api/users")


@user_blueprint.route("/<int:user_id>", methods=["PATCH"])
@user_blueprint.arguments(UpdateUserSchema, location="json")
@user_blueprint.response(HTTPStatus.OK, UserSchema)
@jwt_required()
@user_access_required
def update_user(json_data, user_id):
    current_user.update(json_data, commit=True)
    return current_user
