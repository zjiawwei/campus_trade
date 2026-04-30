from flask import Blueprint

bp = Blueprint("order", __name__, url_prefix="/orders")

from app.blueprints.order import routes  # noqa: E402, F401
