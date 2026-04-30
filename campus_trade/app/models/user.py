from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(32), nullable=True)
    avatar = db.Column(db.String(256), default="default.jpg")
    campus = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(16), default="user")
    credit_score = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    products = db.relationship("Product", back_populates="seller", lazy="dynamic")
    bought_orders = db.relationship(
        "Order", foreign_keys="Order.buyer_id", back_populates="buyer", lazy="dynamic"
    )
    sold_orders = db.relationship(
        "Order", foreign_keys="Order.seller_id", back_populates="seller", lazy="dynamic"
    )
    sent_messages = db.relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender", lazy="dynamic"
    )
    received_messages = db.relationship(
        "Message", foreign_keys="Message.receiver_id", back_populates="receiver", lazy="dynamic"
    )
    favorites = db.relationship("Favorite", back_populates="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User id={self.id}>"
