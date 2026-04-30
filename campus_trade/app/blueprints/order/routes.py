from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.order import bp
from app.extensions import db
from app.models.order import Order
from app.models.product import Product
from app.services.order_service import (
    create_order, get_order, confirm_order, cancel_order, complete_order,
    get_user_bought_orders, get_user_sold_orders,
)


@bp.route("/")
@login_required
def my_orders():
    """Show user's orders (both bought and sold)."""
    tab = request.args.get("tab", "bought")
    page = request.args.get("page", 1, type=int)

    if tab == "sold":
        orders = get_user_sold_orders(current_user.id, page=page)
    else:
        orders = get_user_bought_orders(current_user.id, page=page)

    return render_template(
        "order/list.html",
        orders=orders,
        tab=tab,
    )


@bp.route("/<int:order_id>")
@login_required
def detail(order_id):
    """Order detail page."""
    order = get_order(order_id)
    if order is None:
        flash("订单不存在。", "danger")
        return redirect(url_for("order.my_orders"))

    if order.buyer_id != current_user.id and order.seller_id != current_user.id:
        flash("无权查看该订单。", "danger")
        return redirect(url_for("order.my_orders"))

    return render_template("order/detail.html", order=order)


@bp.route("/<int:order_id>/confirm")
@login_required
def confirm(order_id):
    """Seller confirms an order."""
    order = get_order(order_id)
    if order is None:
        flash("订单不存在。", "danger")
        return redirect(url_for("order.my_orders"))

    success, message = confirm_order(order, current_user)
    flash(message, "success" if success else "danger")
    return redirect(url_for("order.detail", order_id=order_id))


@bp.route("/<int:order_id>/cancel")
@login_required
def cancel(order_id):
    """Cancel an order."""
    order = get_order(order_id)
    if order is None:
        flash("订单不存在。", "danger")
        return redirect(url_for("order.my_orders"))

    success, message = cancel_order(order, current_user)
    flash(message, "success" if success else "danger")
    return redirect(url_for("order.detail", order_id=order_id))


@bp.route("/<int:order_id>/complete")
@login_required
def complete(order_id):
    """Complete an order (seller marks as done)."""
    order = get_order(order_id)
    if order is None:
        flash("订单不存在。", "danger")
        return redirect(url_for("order.my_orders"))

    success, message = complete_order(order, current_user)
    flash(message, "success" if success else "danger")
    return redirect(url_for("order.detail", order_id=order_id))


@bp.route("/<int:order_id>/review", methods=["GET", "POST"])
@login_required
def review(order_id):
    """Create a review for a completed order."""
    from app.services.review_service import create_review, has_reviewed, get_order_reviews
    from app.blueprints.order.review_forms import ReviewForm

    order = get_order(order_id)
    if order is None:
        flash("订单不存在。", "danger")
        return redirect(url_for("order.my_orders"))

    if order.status != "completed":
        flash("只能评价已完成的订单。", "warning")
        return redirect(url_for("order.detail", order_id=order_id))

    if has_reviewed(order_id, current_user.id):
        flash("您已经评价过该订单了。", "warning")
        return redirect(url_for("order.detail", order_id=order_id))

    form = ReviewForm()
    if form.validate_on_submit():
        review_obj, error = create_review(
            order_id=order_id,
            reviewer_id=current_user.id,
            rating=form.rating.data,
            content=form.content.data or None,
        )
        if error:
            flash(error, "danger")
        else:
            flash("评价提交成功！", "success")
            return redirect(url_for("order.detail", order_id=order_id))

    reviews = get_order_reviews(order_id)
    return render_template(
        "order/review.html",
        form=form,
        order=order,
        reviews=reviews,
    )
