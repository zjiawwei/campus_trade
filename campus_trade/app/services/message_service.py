from app.extensions import db
from app.models.message import Message
from sqlalchemy import or_, and_, func


def send_message(sender_id, receiver_id, content, product_id=None):
    """Send a message. Returns the Message object."""
    msg = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        product_id=product_id,
    )
    db.session.add(msg)
    db.session.commit()
    return msg


def get_conversation(user_id, other_user_id, product_id=None, page=1, per_page=50):
    """Get messages between two users (optionally for a specific product)."""
    filters = [
        or_(
            and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == user_id),
        )
    ]
    if product_id:
        filters.append(Message.product_id == product_id)

    return (
        Message.query
        .filter(*filters)
        .order_by(Message.created_at.asc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )


def get_conversations(user_id, page=1, per_page=20):
    """Get list of conversations for a user.
    Returns the most recent message per conversation partner+product pair.
    """
    # Subquery: get the latest message id for each conversation
    sub = (
        db.session.query(
            func.max(Message.id).label("max_id")
        )
        .filter(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id,
            )
        )
        .group_by(
            func.min(Message.sender_id, Message.receiver_id),
            func.max(Message.sender_id, Message.receiver_id),
            func.coalesce(Message.product_id, 0),
        )
        .subquery()
    )

    return (
        Message.query
        .filter(Message.id.in_(db.session.query(sub.c.max_id)))
        .order_by(Message.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )


def mark_as_read(user_id, sender_id=None):
    """Mark messages as read for a user, optionally from a specific sender."""
    query = Message.query.filter_by(receiver_id=user_id, is_read=False)
    if sender_id:
        query = query.filter_by(sender_id=sender_id)
    query.update({"is_read": True}, synchronize_session=False)
    db.session.commit()


def get_unread_count(user_id):
    """Get unread message count."""
    return Message.query.filter_by(receiver_id=user_id, is_read=False).count()
