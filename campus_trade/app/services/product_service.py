from app.extensions import db
from app.models.product import Product, ProductImage
from app.models.favorite import Favorite


def create_product(seller_id, title, description, price, category_id, campus,
                   condition="used", original_price=None):
    """Create a new product listing. Returns the Product object."""
    product = Product(
        seller_id=seller_id,
        title=title,
        description=description,
        price=price,
        original_price=original_price,
        category_id=category_id,
        campus=campus,
        condition=condition,
    )
    db.session.add(product)
    db.session.commit()
    return product


def update_product(product, **kwargs):
    """Update product fields. Returns the updated Product."""
    updatable = {"title", "description", "price", "original_price",
                 "category_id", "campus", "condition", "status"}
    for field, value in kwargs.items():
        if field in updatable and value is not None:
            setattr(product, field, value)
    db.session.commit()
    return product


def withdraw_product(product):
    """Withdraw a product from sale."""
    if product.status == "active":
        product.status = "withdrawn"
        db.session.commit()
    return product


def delete_product(product):
    """Permanently delete a product and its images."""
    db.session.delete(product)
    db.session.commit()


def get_product(product_id):
    """Get a product by ID."""
    return db.session.get(Product, product_id)


def increment_view_count(product):
    """Increment product view count."""
    product.view_count = (product.view_count or 0) + 1
    db.session.commit()


def search_products(category_id=None, keyword=None, campus=None,
                    sort_by="latest", page=1, per_page=12):
    """Search and filter products with pagination."""
    query = Product.query.filter_by(status="active")

    if category_id:
        query = query.filter_by(category_id=category_id)

    if keyword:
        query = query.filter(
            Product.title.ilike(f"%{keyword}%")
            | Product.description.ilike(f"%{keyword}%")
        )

    if campus:
        query = query.filter_by(campus=campus)

    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_user_products(user_id, status=None, page=1, per_page=12):
    """Get products owned by a specific user."""
    query = Product.query.filter_by(seller_id=user_id)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )


def add_product_image(product_id, filename, is_cover=False):
    """Add an image to a product."""
    image = ProductImage(
        product_id=product_id,
        filename=filename,
        is_cover=is_cover,
    )
    db.session.add(image)
    db.session.commit()
    return image


def set_cover_image(product_id, image_id):
    """Set a specific image as the cover for a product."""
    # Unset all covers
    ProductImage.query.filter_by(product_id=product_id).update({"is_cover": False})
    # Set the new cover
    image = db.session.get(ProductImage, image_id)
    if image:
        image.is_cover = True
    db.session.commit()
    return image


def delete_product_image(image_id):
    """Delete a product image."""
    image = db.session.get(ProductImage, image_id)
    if image:
        db.session.delete(image)
        db.session.commit()
    return image


def toggle_favorite(user_id, product_id):
    """Toggle favorite status. Returns (is_favorited_now, favorite_count)."""
    existing = Favorite.query.filter_by(
        user_id=user_id, product_id=product_id
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return False, Favorite.query.filter_by(product_id=product_id).count()
    else:
        fav = Favorite(user_id=user_id, product_id=product_id)
        db.session.add(fav)
        db.session.commit()
        return True, Favorite.query.filter_by(product_id=product_id).count()


def is_favorited(user_id, product_id):
    """Check if a user has favorited a product."""
    return Favorite.query.filter_by(
        user_id=user_id, product_id=product_id
    ).first() is not None


def get_user_favorites(user_id, page=1, per_page=12):
    """Get a user's favorited products with pagination."""
    return (
        Product.query
        .join(Favorite, Favorite.product_id == Product.id)
        .filter(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
