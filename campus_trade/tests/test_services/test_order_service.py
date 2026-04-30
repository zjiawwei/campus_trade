"""Unit tests for order service layer."""

import pytest
from app.services.user_service import create_user
from app.services.product_service import create_product
from app.services.order_service import (
    create_order, get_order, confirm_order, cancel_order, complete_order,
)
from app.extensions import db
from app.models.category import Category


class TestOrderService:
    """Test order service business logic."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        with app.app_context():
            db.create_all()
            cat = Category(name="电子产品", sort_order=1)
            db.session.add(cat)
            db.session.commit()
            self.cat_id = cat.id
            seller = create_user("oseller", "OS01", "Pass1234", "广州新港校区")
            buyer = create_user("obuyer", "OB01", "Pass1234", "广州琶洲校区")
            self.seller_id = seller.id
            self.buyer_id = buyer.id

    def test_create_order_success(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "测试商品", "描述用于测试", 50.00, self.cat_id, "广州新港校区")
            order, error = create_order(self.buyer_id, p.id, trade_location="校门口")
            assert error is None
            assert order is not None
            assert float(order.amount) == 50.00
            assert order.status == "pending"

    def test_cannot_buy_own_product(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "自卖", "描述用于测试", 10.00, self.cat_id, "广州新港校区")
            order, error = create_order(self.seller_id, p.id)
            assert order is None
            assert "自己" in error

    def test_cannot_buy_reserved_product(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "已预定", "描述用于测试", 10.00, self.cat_id, "广州新港校区")
            create_order(self.buyer_id, p.id)
            # Second buyer tries
            buyer2 = create_user("obuyer2", "OB02", "Pass1234", "广州琶洲校区")
            order, error = create_order(buyer2.id, p.id)
            assert order is None
            assert "不可购买" in error

    def test_confirm_order(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "确认测试", "描述用于测试", 20.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            from app.models.user import User
            seller = db.session.get(User, self.seller_id)
            success, msg = confirm_order(order, seller)
            assert success is True
            assert order.status == "confirmed"

    def test_confirm_order_wrong_user(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "权限测试", "描述用于测试", 20.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            from app.models.user import User
            buyer = db.session.get(User, self.buyer_id)
            success, msg = confirm_order(order, buyer)
            assert success is False

    def test_cancel_order_restores_product(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "取消测试", "描述用于测试", 30.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            assert p.status == "reserved"
            from app.models.user import User
            buyer = db.session.get(User, self.buyer_id)
            success, msg = cancel_order(order, buyer)
            assert success is True
            assert order.status == "cancelled"
            assert p.status == "active"  # Restored

    def test_complete_order(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "完成测试", "描述用于测试", 40.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            from app.models.user import User
            seller = db.session.get(User, self.seller_id)
            confirm_order(order, seller)
            complete_order(order, seller)
            assert order.status == "completed"
            assert p.status == "sold"

    def test_cannot_complete_unconfirmed(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "跳过确认", "描述用于测试", 40.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            from app.models.user import User
            seller = db.session.get(User, self.seller_id)
            success, msg = complete_order(order, seller)
            assert success is False
            assert "需要先确认" in msg
