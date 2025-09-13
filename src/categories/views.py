from flask_smorest import Blueprint

from src.categories.schemas import CategorySchema
from src.categories.models import Category

category_blueprint = Blueprint(
    "category", __name__, url_prefix="/users/<int:user_id>/categories"
)


@category_blueprint.route("/", methods=["GET"])
@category_blueprint.response(200, CategorySchema(many=True))
def get_categories(user_id):
    return Category.filter(user_id=user_id)
