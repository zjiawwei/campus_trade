from datetime import datetime, timezone
from app.extensions import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship("User", back_populates="favorites")
    product = db.relationship("Product", back_populates="favorites")

    # Constraints
    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_favorites_user_product"),
    )

    def __repr__(self):
        return f"<Favorite user={self.user_id} product={self.product_id}>"
