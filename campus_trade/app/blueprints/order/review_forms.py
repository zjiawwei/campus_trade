from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length
from app.utils.constants import RATING_MIN, RATING_MAX


class ReviewForm(FlaskForm):
    rating = RadioField(
        "评分",
        choices=[
            (5, "⭐⭐⭐⭐⭐ 非常好"),
            (4, "⭐⭐⭐⭐ 好"),
            (3, "⭐⭐⭐ 一般"),
            (2, "⭐⭐ 较差"),
            (1, "⭐ 很差"),
        ],
        validators=[DataRequired(message="请选择评分")],
        coerce=int,
        default=5,
    )
    content = TextAreaField(
        "评价内容 (选填)",
        validators=[Length(max=512, message="评价内容过长")],
    )
    submit = SubmitField("提交评价")
