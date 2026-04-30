from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, Optional


class OrderForm(FlaskForm):
    trade_location = StringField(
        "交易地点",
        validators=[
            Length(max=128, message="交易地点过长"),
        ],
    )
    buyer_message = TextAreaField(
        "留言 (选填)",
        validators=[
            Length(max=256, message="留言过长"),
        ],
    )
    submit = SubmitField("确认下单")
