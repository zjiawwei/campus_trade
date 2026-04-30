"""Integration tests for order blueprint routes."""

import json
import pytest
from app.services.user_service import create_user
from app.extensions import db
from app.models.category import Category


class TestOrderRoutes:
    """Test order route endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        with app.app_context():
            db.create_all()
            cat = Category(name="电子产品", sort_order=1)
            db.session.add(cat)
            db.session.commit()
            self.cat_id = cat.id
            seller = create_user("rseller", "RO01", "Pass1234", "广州新港校区")
            buyer = create_user("rbuyer", "RO02", "Pass1234", "广州琶洲校区")
            self.seller_id = seller.id
            self.buyer_id = buyer.id

    def _create_product(self, app, **kwargs):
        from app.services.product_service import create_product
        defaults = {
            "seller_id": self.seller_id, "title": "测试商品",
            "description": "描述用于测试订单", "price": 10.00,
            "category_id": self.cat_id, "campus": "广州新港校区",
        }
        defaults.update(kwargs)
        return create_product(**defaults).id

    def test_order_list_requires_login(self, client):
        resp = client.get("/orders/", follow_redirects=True)
        assert "请先登录" in resp.get_data(as_text=True)

    def test_place_order_flow(self, client, app):
        pid = self._create_product(app, title="下单流程测试", price=88.00)

        # Buyer login and place order
        client.post("/auth/login", data={"login_id": "rbuyer", "password": "Pass1234"})
        resp = client.post(f"/products/{pid}/order", data={
            "trade_location": "食堂门口",
            "buyer_message": "测试留言",
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        assert "下单成功" in html
        assert "88.00" in html

        # Buyer sees order in their list
        resp2 = client.get("/orders/?tab=bought")
        assert "下单流程测试" in resp2.get_data(as_text=True)

        # Seller login and confirm
        client.get("/auth/logout")
        client.post("/auth/login", data={"login_id": "rseller", "password": "Pass1234"})
        client.get("/orders/1/confirm", follow_redirects=True)

        # Complete order
        resp3 = client.get("/orders/1/complete", follow_redirects=True)
        assert "已完成" in resp3.get_data(as_text=True)
