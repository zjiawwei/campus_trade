from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app.blueprints.product import bp
from app.extensions import db, csrf
from app.models.product import Product
from app.models.category import Category


@bp.route("/")
def index():
    """Product listing page with optional category filter and keyword search."""
    page = request.args.get("page", 1, type=int)
    category_id = request.args.get("category", type=int)
    seller_id = request.args.get("seller", type=int)
    keyword = request.args.get("q", "").strip()

    query = Product.query

    if seller_id:
        query = query.filter_by(seller_id=seller_id)
    else:
        query = query.filter_by(status="active")

    if category_id:
        query = query.filter_by(category_id=category_id)

    if keyword:
        query = query.filter(
            Product.title.ilike(f"%{keyword}%")
            | Product.description.ilike(f"%{keyword}%")
        )

    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    categories = Category.query.order_by(Category.sort_order).all()

    return render_template(
        "product/index.html",
        products=products,
        categories=categories,
        current_category_id=category_id,
        keyword=keyword,
    )


@bp.route("/<int:product_id>")
def detail(product_id):
    """Product detail page."""
    product = db.session.get(
        Product, product_id,
        options=[joinedload(Product.seller), joinedload(Product.category)],
    )
    if product is None:
        flash("商品不存在或已下架。", "danger")
        return redirect(url_for("product.index"))
    return render_template("product/detail.html", product=product)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new product listing."""
    from app.blueprints.product.forms import ProductForm
    form = ProductForm()
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.sort_order).all()
    ]
    if form.validate_on_submit():
        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            original_price=form.original_price.data or None,
            condition=form.condition.data,
            category_id=form.category_id.data,
            seller_id=current_user.id,
            campus=form.campus.data,
        )
        db.session.add(product)
        db.session.commit()
        flash("商品发布成功！", "success")
        return redirect(url_for("product.detail", product_id=product.id))
    return render_template("product/create.html", form=form)


@bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit(product_id):
    """Edit product listing (owner only)."""
    product = db.session.get(Product, product_id)
    if product is None:
        flash("商品不存在。", "danger")
        return redirect(url_for("product.index"))
    if product.seller_id != current_user.id:
        flash("无权编辑该商品。", "danger")
        return redirect(url_for("product.detail", product_id=product_id))

    from app.blueprints.product.forms import ProductForm
    form = ProductForm(obj=product)
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.sort_order).all()
    ]
    if form.validate_on_submit():
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.original_price = form.original_price.data or None
        product.condition = form.condition.data
        product.category_id = form.category_id.data
        product.campus = form.campus.data
        db.session.commit()
        flash("商品信息已更新。", "success")
        return redirect(url_for("product.detail", product_id=product.id))
    return render_template("product/edit.html", form=form, product=product)


@bp.route("/<int:product_id>/withdraw")
@login_required
def withdraw(product_id):
    """Withdraw a product listing (owner only)."""
    product = db.session.get(Product, product_id)
    if product is None:
        flash("商品不存在。", "danger")
        return redirect(url_for("product.index"))
    if product.seller_id != current_user.id:
        flash("无权操作该商品。", "danger")
        return redirect(url_for("product.detail", product_id=product_id))
    if product.status == "active":
        product.status = "withdrawn"
        db.session.commit()
        flash("商品已下架。", "info")
    return redirect(url_for("product.detail", product_id=product_id))


@bp.route("/<int:product_id>/order", methods=["GET", "POST"])
@login_required
def place_order(product_id):
    """Place an order for a product."""
    from app.services.order_service import create_order
    from app.blueprints.order.forms import OrderForm

    product = db.session.get(Product, product_id)
    if product is None:
        flash("商品不存在。", "danger")
        return redirect(url_for("product.index"))

    if product.seller_id == current_user.id:
        flash("不能购买自己的商品。", "warning")
        return redirect(url_for("product.detail", product_id=product_id))

    if product.status != "active":
        flash("该商品当前不可购买。", "warning")
        return redirect(url_for("product.detail", product_id=product_id))

    form = OrderForm()
    if form.validate_on_submit():
        order, error = create_order(
            buyer_id=current_user.id,
            product_id=product_id,
            trade_location=form.trade_location.data or None,
            buyer_message=form.buyer_message.data or None,
        )
        if error:
            flash(error, "danger")
        else:
            flash("下单成功！请等待卖家确认。", "success")
            return redirect(url_for("order.detail", order_id=order.id))

    return render_template("product/order.html", product=product, form=form)


@bp.route("/<int:product_id>/fav-status")
def fav_status(product_id):
    """Get favorite status and count for a product."""
    from app.services.product_service import is_favorited
    from app.models.favorite import Favorite

    fav_count = Favorite.query.filter_by(product_id=product_id).count()
    if current_user.is_authenticated:
        fav = is_favorited(current_user.id, product_id)
        return jsonify({"is_favorited": fav, "count": fav_count})
    return jsonify({"is_favorited": False, "count": fav_count})


@bp.route("/<int:product_id>/toggle-fav", methods=["POST"])
@login_required
@csrf.exempt
def toggle_fav(product_id):
    """Toggle favorite status for a product. Returns JSON."""
    from app.services.product_service import toggle_favorite
    is_fav, count = toggle_favorite(current_user.id, product_id)
    return jsonify({"is_favorited": is_fav, "count": count})
