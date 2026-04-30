from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, Regexp
from app.blueprints.auth.forms import CAMPUS_CHOICES


class EditProfileForm(FlaskForm):
    real_name = StringField(
        "真实姓名",
        validators=[Length(max=32, message="姓名过长")],
    )
    phone = StringField(
        "手机号",
        validators=[
            Length(max=20, message="手机号过长"),
            Regexp(r"^[0-9\-]*$", message="手机号格式不正确"),
        ],
    )
    campus = SelectField("校区")
    submit = SubmitField("保存修改")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campus.choices = CAMPUS_CHOICES


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "当前密码",
        validators=[DataRequired(message="请输入当前密码")],
    )
    new_password = PasswordField(
        "新密码",
        validators=[
            DataRequired(message="请输入新密码"),
            Length(min=6, max=128, message="密码长度需在 6-128 个字符之间"),
        ],
    )
    confirm_password = PasswordField(
        "确认新密码",
        validators=[
            DataRequired(message="请确认新密码"),
            EqualTo("new_password", message="两次输入的密码不一致"),
        ],
    )
    submit = SubmitField("修改密码")
