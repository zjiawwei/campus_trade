from flask import Blueprint

bp = Blueprint("product", __name__, url_prefix="/products")

from app.blueprints.product import routes  # noqa: E402, F401
