from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import bp
from app.blueprints.auth.forms import LoginForm, RegistrationForm
from app.services.user_service import create_user, authenticate_user


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        create_user(
            username=form.username.data,
            student_id=form.student_id.data,
            password=form.password.data,
            campus=form.campus.data,
            real_name=form.real_name.data or "",
            phone=form.phone.data or "",
        )
        flash("注册成功！请登录。", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(form.login_id.data, form.password.data)
        if user:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            flash("登录成功！", "success")
            return redirect(next_page or url_for("main.index"))
        flash("用户名或密码错误，请重试。", "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已成功退出登录。", "info")
    return redirect(url_for("main.index"))
