"""Unit tests for message service layer."""

import pytest
from app.services.user_service import create_user
from app.services.message_service import (
    send_message, get_conversation, get_conversations,
    get_unread_count, mark_as_read,
)
from app.extensions import db


class TestMessageService:
    """Test message service business logic."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        with app.app_context():
            self.sender = create_user("msender", "MS01", "Pass1234", "广州新港校区")
            self.receiver = create_user("mrecv", "MR01", "Pass1234", "广州琶洲校区")
            self.sender_id = self.sender.id
            self.receiver_id = self.receiver.id

    def test_send_message(self, app):
        with app.app_context():
            msg = send_message(self.sender_id, self.receiver_id, "测试消息")
            assert msg.id is not None
            assert msg.content == "测试消息"
            assert msg.is_read is False

    def test_get_conversation(self, app):
        with app.app_context():
            send_message(self.sender_id, self.receiver_id, "你好")
            send_message(self.receiver_id, self.sender_id, "你好，在的")
            msgs = get_conversation(self.sender_id, self.receiver_id)
            assert len(msgs.items) == 2

    def test_unread_count(self, app):
        with app.app_context():
            send_message(self.sender_id, self.receiver_id, "未读1")
            send_message(self.sender_id, self.receiver_id, "未读2")
            assert get_unread_count(self.receiver_id) == 2
            assert get_unread_count(self.sender_id) == 0

    def test_mark_as_read(self, app):
        with app.app_context():
            send_message(self.sender_id, self.receiver_id, "msg1")
            send_message(self.sender_id, self.receiver_id, "msg2")
            mark_as_read(self.receiver_id, sender_id=self.sender_id)
            assert get_unread_count(self.receiver_id) == 0

    def test_get_conversations(self, app):
        with app.app_context():
            send_message(self.sender_id, self.receiver_id, "对话1")
            # Create a third user for a second conversation
            user3 = create_user("mthird", "MT01", "Pass1234", "广州新港校区")
            send_message(user3.id, self.receiver_id, "对话2")
            convs = get_conversations(self.receiver_id)
            assert len(convs.items) >= 2
