from datetime import datetime, timezone
from app.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(16), default="pending")
    trade_location = db.Column(db.String(128), nullable=True)
    trade_time = db.Column(db.DateTime, nullable=True)
    buyer_message = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    buyer = db.relationship("User", foreign_keys=[buyer_id], back_populates="bought_orders")
    seller = db.relationship("User", foreign_keys=[seller_id], back_populates="sold_orders")
    product = db.relationship("Product", back_populates="orders")
    review = db.relationship("Review", back_populates="order", uselist=False)

    # Indexes
    __table_args__ = (
        db.Index("ix_orders_buyer", "buyer_id"),
        db.Index("ix_orders_seller", "seller_id"),
        db.Index("ix_orders_status", "status"),
    )

    VALID_STATUSES = ("pending", "confirmed", "completed", "cancelled")
    ALLOWED_TRANSITIONS = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"completed", "cancelled"},
        "completed": set(),
        "cancelled": set(),
    }

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, set())

    def __repr__(self):
        return f"<Order id={self.id}>"


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = db.relationship("Order", back_populates="review")

    def __repr__(self):
        return f"<Review id={self.id}>"
