from datetime import datetime, timezone
from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2), nullable=True)
    condition = db.Column(
        db.String(16),
        nullable=False,
        default="used",
    )
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    campus = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(16), default="active")
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    images = db.relationship(
        "ProductImage", back_populates="product", lazy="dynamic", cascade="all, delete-orphan"
    )
    seller = db.relationship("User", back_populates="products")
    category = db.relationship("Category", back_populates="products")
    favorites = db.relationship("Favorite", back_populates="product", lazy="dynamic")
    orders = db.relationship("Order", back_populates="product", lazy="dynamic")

    # Indexes
    __table_args__ = (
        db.Index("ix_products_status_category", "status", "category_id"),
        db.Index("ix_products_seller", "seller_id"),
        db.Index("ix_products_campus", "campus"),
    )

    @property
    def cover_image(self):
        cover = (
            ProductImage.query
            .filter_by(product_id=self.id, is_cover=True)
            .first()
        )
        if cover:
            return cover.filename
        first_image = (
            ProductImage.query
            .filter_by(product_id=self.id)
            .order_by(ProductImage.sort_order)
            .first()
        )
        return first_image.filename if first_image else None

    def __repr__(self):
        return f"<Product id={self.id}>"


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    filename = db.Column(db.String(256), nullable=False)
    is_cover = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    product = db.relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage id={self.id}>"
