from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
)
from app.utils.constants import PRODUCT_CONDITIONS
from app.blueprints.auth.forms import CAMPUS_CHOICES


class ProductForm(FlaskForm):
    title = StringField(
        "商品标题",
        validators=[
            DataRequired(message="请输入商品标题"),
            Length(min=2, max=128, message="标题长度需在 2-128 个字符之间"),
        ],
    )
    description = TextAreaField(
        "商品描述",
        validators=[
            DataRequired(message="请输入商品描述"),
            Length(min=10, max=5000, message="描述长度需在 10-5000 个字符之间"),
        ],
    )
    price = DecimalField(
        "售价 (元)",
        validators=[
            DataRequired(message="请输入售价"),
            NumberRange(min=0.01, max=999999.99, message="价格须在 0.01 - 999999.99 之间"),
        ],
    )
    original_price = DecimalField(
        "原价 (元, 选填)",
        validators=[
            Optional(),
            NumberRange(min=0, max=999999.99, message="原价须在 0 - 999999.99 之间"),
        ],
    )
    condition = SelectField(
        "商品成色",
        choices=[(k, v) for k, v in PRODUCT_CONDITIONS.items()],
        validators=[DataRequired(message="请选择商品成色")],
    )
    category_id = SelectField(
        "商品分类",
        choices=[],  # Set dynamically in route
        validators=[DataRequired(message="请选择分类")],
        coerce=int,
    )
    campus = SelectField(
        "交易校区",
        validators=[DataRequired(message="请选择校区")],
    )
    submit = SubmitField("发布商品")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campus.choices = [(c[0], c[1]) for c in CAMPUS_CHOICES if c[0]]
