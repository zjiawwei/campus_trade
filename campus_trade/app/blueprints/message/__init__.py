from flask import Blueprint

bp = Blueprint("message", __name__, url_prefix="/messages")

from app.blueprints.message import routes  # noqa: E402, F401
