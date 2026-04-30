from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.message import bp
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.services.message_service import (
    send_message, get_conversation, get_conversations, mark_as_read,
    get_unread_count,
)


@bp.route("/")
@login_required
def list_conversations():
    """List all conversations for the current user."""
    page = request.args.get("page", 1, type=int)
    conversations = get_conversations(current_user.id, page=page)
    unread = get_unread_count(current_user.id)
    return render_template(
        "message/list.html",
        conversations=conversations,
        unread_total=unread,
    )


@bp.route("/unread-count")
@login_required
def unread_count_api():
    """API: Get unread message count for navbar badge."""
    return jsonify({"count": get_unread_count(current_user.id)})


@bp.route("/with/<int:user_id>")
@login_required
def conversation(user_id):
    """View conversation with a specific user."""
    product_id = request.args.get("product_id", type=int)
    page = request.args.get("page", 1, type=int)

    other_user = db.session.get(User, user_id)
    if other_user is None:
        flash("用户不存在。", "danger")
        return redirect(url_for("message.list_conversations"))

    product = None
    if product_id:
        product = db.session.get(Product, product_id)

    # Mark messages from this user as read
    mark_as_read(current_user.id, sender_id=user_id)

    messages = get_conversation(
        current_user.id, user_id, product_id=product_id, page=page
    )

    return render_template(
        "message/conversation.html",
        messages=messages,
        other_user=other_user,
        product=product,
        product_id=product_id,
    )


@bp.route("/with/<int:user_id>/send", methods=["POST"])
@login_required
def send(user_id):
    """Send a message to a user."""
    content = request.form.get("content", "").strip()
    product_id = request.form.get("product_id", type=int)

    if not content:
        flash("消息内容不能为空。", "warning")
    elif len(content) > 2000:
        flash("消息内容过长。", "warning")
    else:
        send_message(
            sender_id=current_user.id,
            receiver_id=user_id,
            content=content,
            product_id=product_id,
        )

    return redirect(url_for(
        "message.conversation",
        user_id=user_id,
        product_id=product_id,
    ))
