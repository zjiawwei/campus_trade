from flask import render_template
from app.blueprints.main import bp
from app.models.category import Category
from app.models.product import Product


@bp.route("/")
def index():
    categories = Category.query.order_by(Category.sort_order).all()
    latest_products = (
        Product.query
        .filter_by(status="active")
        .order_by(Product.created_at.desc())
        .limit(6)
        .all()
    )
    return render_template(
        "main/index.html",
        categories=categories,
        latest_products=latest_products,
    )
