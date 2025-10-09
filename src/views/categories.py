from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from http import HTTPStatus

from src.schemas.categories import (
    CategorySchema,
    CategorySummarySchema,
    CategoryListRequestSchema,
    UpdateCategorySchema,
)
from src.models.categories import Category
from src.models.users import User
from src.extensions import db
from src.views.utils import user_access_required


category_blueprint = Blueprint(
    "category", __name__, url_prefix="/users/<int:user_id>/categories"
)


@category_blueprint.route("/", methods=["GET"])
@category_blueprint.arguments(CategoryListRequestSchema, location="query")
@category_blueprint.response(200)
@jwt_required()
@user_access_required
def get_all_categories(args, user_id):
    summary = args.get("summary", False)
    schema = CategorySummarySchema if summary else CategorySchema
    return schema(many=True).dump(Category.filter(user_id=user_id))


@category_blueprint.route("/<int:category_id>", methods=["GET"])
@category_blueprint.response(200, CategorySchema)
@jwt_required()
@user_access_required
def get_category(user_id, category_id):
    return Category.find_category_by_user_and_id_or_404(user_id, category_id)


@category_blueprint.route("/", methods=["POST"])
@category_blueprint.arguments(CategorySchema, location="json")
@category_blueprint.response(201, CategorySchema)
@jwt_required()
@user_access_required
def create_category(json_data, user_id):
    User.get_or_404(user_id)
    category = Category.create({**json_data, "user_id": user_id}, commit=True)
    return category


@category_blueprint.route("/<int:category_id>", methods=["PUT"])
@category_blueprint.arguments(UpdateCategorySchema, location="json")
@category_blueprint.response(200, CategorySchema)
@jwt_required()
@user_access_required
def update_category(json_data, user_id, category_id):
    category = Category.find_category_by_user_and_id_or_404(
        user_id, category_id
    )
    category.update(json_data, commit=True)
    return category


@category_blueprint.route("/<int:category_id>", methods=["DELETE"])
@category_blueprint.response(HTTPStatus.NO_CONTENT)
@jwt_required()
@user_access_required
def delete_category(user_id, category_id):
    category = Category.find_category_by_user_and_id_or_404(
        user_id, category_id
    )
    for note in category.notes:
        note.update({"category_id": None}, commit=False)
    db.session.commit()
    category.soft_delete(commit=True)
    return "", HTTPStatus.NO_CONTENT
