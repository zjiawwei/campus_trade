from app.extensions import db
from app.models.order import Order, Review
from app.models.user import User


def create_review(order_id, reviewer_id, rating, content=None):
    """Create a review for a completed order. Returns (review, error)."""
    order = db.session.get(Order, order_id)
    if order is None:
        return None, "订单不存在。"

    if order.status != "completed":
        return None, "只能对已完成的订单进行评价。"

    if reviewer_id not in (order.buyer_id, order.seller_id):
        return None, "无权评价该订单。"

    # Check for existing review
    existing = Review.query.filter_by(order_id=order_id, reviewer_id=reviewer_id).first()
    if existing:
        return None, "您已经评价过该订单了。"

    target_user_id = (
        order.seller_id if reviewer_id == order.buyer_id else order.buyer_id
    )

    review = Review(
        order_id=order_id,
        reviewer_id=reviewer_id,
        target_user_id=target_user_id,
        rating=rating,
        content=content,
    )
    db.session.add(review)

    # Update credit score of target user
    target = db.session.get(User, target_user_id)
    if target:
        # Average: (current * count_implicit + new) / (count_implicit + 1)
        existing_avg = (
            db.session.query(db.func.avg(Review.rating))
            .filter_by(target_user_id=target_user_id)
            .scalar() or 0
        )
        target.credit_score = int(existing_avg * 20)  # Scale to 0-100

    db.session.commit()
    return review, None


def get_order_reviews(order_id):
    """Get all reviews for an order."""
    return Review.query.filter_by(order_id=order_id).all()


def get_user_reviews(user_id, page=1, per_page=10):
    """Get paginated reviews targeting a user."""
    return (
        Review.query
        .filter_by(target_user_id=user_id)
        .order_by(Review.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )


def has_reviewed(order_id, user_id):
    """Check if a user has already reviewed an order."""
    return Review.query.filter_by(
        order_id=order_id, reviewer_id=user_id
    ).first() is not None
