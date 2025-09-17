from flask_smorest import Blueprint

from src.categories.schemas import (
    CategorySchema,
    CategorySummarySchema,
    CategoryListRequestSchema,
    UpdateCategorySchema,
)
from src.categories.models import Category
from src.users.models import User
from src.extensions import db


category_blueprint = Blueprint(
    "category", __name__, url_prefix="/users/<int:user_id>/categories"
)


@category_blueprint.route("/", methods=["GET"])
@category_blueprint.arguments(CategoryListRequestSchema, location="query")
@category_blueprint.response(200)
def get_all_categories(args, user_id):
    summary = args.get("summary", False)
    schema = CategorySummarySchema if summary else CategorySchema
    return schema(many=True).dump(Category.filter(user_id=user_id))


@category_blueprint.route("/<int:category_id>", methods=["GET"])
@category_blueprint.response(200, CategorySchema)
def get_category(user_id, category_id):
    return Category.find_category_by_user_and_id_or_404(user_id, category_id)


@category_blueprint.route("/", methods=["POST"])
@category_blueprint.arguments(CategorySchema, location="json")
@category_blueprint.response(201, CategorySchema)
def create_category(
    json_data, user_id
):  # All need to validate identity of user
    User.get_or_404(user_id)
    category = Category.create({**json_data, "user_id": user_id}, commit=True)
    return category


@category_blueprint.route("/<int:category_id>", methods=["PUT"])
@category_blueprint.arguments(UpdateCategorySchema, location="json")
@category_blueprint.response(200, CategorySchema)
def update_category(json_data, user_id, category_id):
    category = Category.find_category_by_user_and_id_or_404(
        user_id, category_id
    )
    category.update(json_data, commit=True)
    return category


@category_blueprint.route("/<int:category_id>", methods=["DELETE"])
@category_blueprint.response(204)
def delete_category(user_id, category_id):
    category = Category.find_category_by_user_and_id_or_404(
        user_id, category_id
    )
    for note in category.notes:
        note.update({"category_id": None}, commit=False)
    db.session.commit()
    category.soft_delete(commit=True)
    return "", 204
