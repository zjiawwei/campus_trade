from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SelectField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    Regexp,
    ValidationError,
)
from app.services.user_service import (
    get_user_by_username,
    get_user_by_email,
    get_user_by_student_id,
)

CAMPUS_CHOICES = [
    ("", "请选择校区"),
    ("广州新港校区", "广州新港校区"),
    ("广州琶洲校区", "广州琶洲校区"),
    ("佛山南海校区", "佛山南海校区"),
]


class LoginForm(FlaskForm):
    login_id = StringField(
        "用户名 / 邮箱",
        validators=[
            DataRequired(message="请输入用户名或邮箱"),
            Length(max=128, message="输入过长"),
        ],
    )
    password = PasswordField(
        "密码",
        validators=[
            DataRequired(message="请输入密码"),
        ],
    )
    remember_me = BooleanField("记住我")
    submit = SubmitField("登录")


class RegistrationForm(FlaskForm):
    username = StringField(
        "用户名",
        validators=[
            DataRequired(message="请输入用户名"),
            Length(min=3, max=64, message="用户名长度需在 3-64 个字符之间"),
            Regexp(
                r"^[a-zA-Z0-9_\u4e00-\u9fff]+$",
                message="用户名只能包含字母、数字、下划线和中文",
            ),
        ],
    )
    student_id = StringField(
        "学号",
        validators=[
            DataRequired(message="请输入学号"),
            Length(min=3, max=20, message="学号长度需在 3-20 个字符之间"),
            Regexp(r"^[a-zA-Z0-9]+$", message="学号只能包含字母和数字"),
        ],
    )
    email = StringField(
        "邮箱",
        validators=[
            DataRequired(message="请输入邮箱"),
            Email(message="请输入有效的邮箱地址"),
            Length(max=128, message="邮箱地址过长"),
        ],
    )
    phone = StringField(
        "手机号 (选填)",
        validators=[
            Length(max=20, message="手机号过长"),
            Regexp(r"^[0-9\-]*$", message="手机号格式不正确"),
        ],
    )
    real_name = StringField(
        "真实姓名 (选填)",
        validators=[
            Length(max=32, message="姓名过长"),
        ],
    )
    campus = SelectField(
        "校区",
        validators=[
            DataRequired(message="请选择校区"),
        ],
    )
    password = PasswordField(
        "密码",
        validators=[
            DataRequired(message="请输入密码"),
            Length(min=6, max=128, message="密码长度需在 6-128 个字符之间"),
        ],
    )
    confirm_password = PasswordField(
        "确认密码",
        validators=[
            DataRequired(message="请确认密码"),
            EqualTo("password", message="两次输入的密码不一致"),
        ],
    )
    submit = SubmitField("注册")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campus.choices = CAMPUS_CHOICES

    def validate_username(self, field):
        if get_user_by_username(field.data):
            raise ValidationError("该用户名已被注册")

    def validate_email(self, field):
        if get_user_by_email(field.data):
            raise ValidationError("该邮箱已被注册")

    def validate_student_id(self, field):
        if get_user_by_student_id(field.data):
            raise ValidationError("该学号已被注册")
