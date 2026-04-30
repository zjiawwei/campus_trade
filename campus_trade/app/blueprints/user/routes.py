from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.user import bp
from app.blueprints.user.forms import EditProfileForm, ChangePasswordForm
from app.services.user_service import update_profile, change_password


@bp.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html", user=current_user)


@bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        update_profile(
            current_user,
            real_name=form.real_name.data or "",
            phone=form.phone.data or "",
            campus=form.campus.data,
        )
        flash("个人资料已更新。", "success")
        return redirect(url_for("user.profile"))

    return render_template("user/edit_profile.html", form=form)


@bp.route("/profile/change-password", methods=["GET", "POST"])
@login_required
def change_password_view():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if change_password(
            current_user,
            form.old_password.data,
            form.new_password.data,
        ):
            flash("密码已修改，请使用新密码重新登录。", "success")
            return redirect(url_for("auth.logout"))
        flash("当前密码错误，请重试。", "danger")

    return render_template("user/change_password.html", form=form)
