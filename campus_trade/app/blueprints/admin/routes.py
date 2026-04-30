from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.admin import bp
from app.extensions import db
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.constants import ITEMS_PER_PAGE


@bp.before_request
@login_required
@admin_required
def require_admin():
    """All admin routes require admin role."""
    pass


@bp.route("/")
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    page = request.args.get("page", 1, type=int)
    users = (
        User.query
        .order_by(User.created_at.desc())
        .paginate(page=page, per_page=ITEMS_PER_PAGE, error_out=False)
    )
    return render_template(
        "admin/user_list.html",
        users=users,
        total_users=total_users,
        active_users=active_users,
    )


@bp.route("/users/<int:user_id>")
def user_detail(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("用户不存在。", "danger")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/user_detail.html", user=user)


@bp.route("/users/<int:user_id>/toggle-active")
def toggle_active(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("用户不存在。", "danger")
        return redirect(url_for("admin.dashboard"))

    if user.id == current_user.id:
        flash("不能修改自己的账号状态。", "warning")
        return redirect(url_for("admin.dashboard"))

    user.is_active = not user.is_active
    db.session.commit()
    status = "启用" if user.is_active else "禁用"
    flash(f"用户 {user.username} 已{status}。", "success")
    return redirect(url_for("admin.dashboard"))


@bp.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("用户不存在。", "danger")
        return redirect(url_for("admin.dashboard"))

    if user.id == current_user.id:
        flash("不能删除自己的账号。", "warning")
        return redirect(url_for("admin.dashboard"))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f"用户 {username} 已删除。", "success")
    return redirect(url_for("admin.dashboard"))
