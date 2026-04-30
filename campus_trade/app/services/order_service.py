from datetime import datetime, timezone
from app.extensions import db
from app.models.order import Order
from app.models.product import Product


def create_order(buyer_id, product_id, trade_location=None,
                 trade_time=None, buyer_message=None):
    """Create a new order. Reserves the product. Returns (order, error).

    On success, error is None. On failure, order is None.
    """
    product = db.session.get(Product, product_id)
    if product is None:
        return None, "商品不存在。"

    if product.seller_id == buyer_id:
        return None, "不能购买自己的商品。"

    if product.status != "active":
        return None, "该商品当前不可购买。"

    order = Order(
        buyer_id=buyer_id,
        seller_id=product.seller_id,
        product_id=product_id,
        amount=product.price,
        trade_location=trade_location,
        trade_time=trade_time,
        buyer_message=buyer_message,
        status="pending",
    )

    # Reserve the product
    product.status = "reserved"

    db.session.add(order)
    db.session.commit()
    return order, None


def get_order(order_id):
    """Get an order by ID."""
    return db.session.get(Order, order_id)


def get_user_bought_orders(user_id, page=1, per_page=10):
    """Get paginated orders where user is the buyer."""
    return (
        Order.query
        .filter_by(buyer_id=user_id)
        .order_by(Order.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )


def get_user_sold_orders(user_id, page=1, per_page=10):
    """Get paginated orders where user is the seller."""
    return (
        Order.query
        .filter_by(seller_id=user_id)
        .order_by(Order.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )


def confirm_order(order, user):
    """Seller confirms the order. Returns (success, message)."""
    if order.seller_id != user.id:
        return False, "只有卖家可以确认订单。"

    if order.status != "pending":
        return False, f"当前订单状态为 {order.status}，无法确认。"

    order.status = "confirmed"
    db.session.commit()
    return True, "订单已确认，请等待完成交易。"


def cancel_order(order, user):
    """Cancel a pending or confirmed order. Restores product to active.
    Returns (success, message).
    """
    if user.id not in (order.buyer_id, order.seller_id):
        return False, "无权取消该订单。"

    if order.status not in ("pending", "confirmed"):
        return False, f"当前订单状态为 {order.status}，无法取消。"

    order.status = "cancelled"
    # Restore product
    product = db.session.get(Product, order.product_id)
    if product and product.status == "reserved":
        product.status = "active"
    db.session.commit()
    return True, "订单已取消。"


def complete_order(order, user):
    """Mark order as completed. Only seller can do this from confirmed state.
    Returns (success, message).
    """
    if order.seller_id != user.id:
        return False, "只有卖家可以完成订单。"

    if order.status != "confirmed":
        return False, f"当前订单状态为 {order.status}，需要先确认订单。"

    order.status = "completed"
    # Mark product as sold
    product = db.session.get(Product, order.product_id)
    if product:
        product.status = "sold"
    db.session.commit()
    return True, "交易已完成！"
