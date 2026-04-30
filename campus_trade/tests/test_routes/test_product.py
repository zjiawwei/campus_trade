"""Integration tests for product blueprint routes."""

import json
import pytest
from app.services.user_service import create_user
from app.extensions import db
from app.models.category import Category


class TestProductRoutes:
    """Test product route endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        with app.app_context():
            db.create_all()
            cat = Category(name="电子产品", icon="bi-laptop", sort_order=2)
            db.session.add(cat)
            db.session.commit()
            self.cat_id = cat.id
            seller = create_user(
                "routeseller", "R001", "Pass1234", "广州新港校区"
            )
            buyer = create_user(
                "routebuyer", "R002", "Pass1234", "广州琶洲校区"
            )
            self.seller_id = seller.id
            self.buyer_id = buyer.id

    def _login_as_seller(self, client):
        client.post("/auth/login", data={
            "login_id": "routeseller", "password": "Pass1234"
        })

    def _login_as_buyer(self, client):
        client.post("/auth/login", data={
            "login_id": "routebuyer", "password": "Pass1234"
        })

    def _create_product(self, app, **kwargs):
        from app.services.product_service import create_product
        defaults = {
            "seller_id": self.seller_id,
            "title": "测试商品",
            "description": "商品描述信息测试",
            "price": 10.00,
            "category_id": self.cat_id,
            "campus": "广州新港校区",
        }
        defaults.update(kwargs)
        p = create_product(**defaults)
        return p.id

    def test_product_index_empty(self, client):
        resp = client.get("/products/")
        assert resp.status_code == 200
        assert "浏览商品" in resp.get_data(as_text=True)

    def test_product_index_with_data(self, client, app):
        self._create_product(app, title="展示商品", price=88.00, original_price=100.00)
        resp = client.get("/products/")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "展示商品" in html
        assert "88.00" in html

    def test_product_detail(self, client, app):
        p = self._create_product(app, title="详情测试", price=55.00)
        resp = client.get(f"/products/{p}")
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "详情测试" in html
        assert "55.00" in html

    def test_create_product_requires_login(self, client):
        resp = client.get("/products/create", follow_redirects=True)
        assert "请先登录" in resp.get_data(as_text=True)

    def test_create_product_success(self, client):
        self._login_as_seller(client)
        resp = client.post("/products/create", data={
            "title": "新发布的商品",
            "description": "这是一个测试商品的详细描述，超过十个字",
            "price": "42.00",
            "condition": "used",
            "category_id": str(self.cat_id),
            "campus": "广州新港校区",
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert "新发布的商品" in html
        assert "42.00" in html

    def test_edit_own_product(self, client, app):
        p = self._create_product(app, title="待编辑")
        self._login_as_seller(client)

        resp = client.post(f"/products/{p}/edit", data={
            "title": "已编辑的标题",
            "description": "更新后的描述信息测试，超过十个字了",
            "price": "35.00",
            "condition": "like_new",
            "category_id": str(self.cat_id),
            "campus": "广州琶洲校区",
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        assert "已编辑的标题" in html
        assert "35.00" in html

    def test_edit_non_owner_blocked(self, client, app):
        p = self._create_product(app, title="别人的")
        self._login_as_buyer(client)
        resp = client.get(f"/products/{p}/edit", follow_redirects=True)
        assert "无权编辑" in resp.get_data(as_text=True)

    def test_withdraw_product(self, client, app):
        p = self._create_product(app, title="要下架的")
        self._login_as_seller(client)
        resp = client.get(f"/products/{p}/withdraw", follow_redirects=True)
        assert "已下架" in resp.get_data(as_text=True)

    def test_toggle_favorite(self, client, app):
        p = self._create_product(app, title="收藏商品")
        self._login_as_buyer(client)

        resp = client.post(f"/products/{p}/toggle-fav")
        data = json.loads(resp.get_data(as_text=True))
        assert data["is_favorited"] is True
        assert data["count"] == 1

        resp2 = client.post(f"/products/{p}/toggle-fav")
        data2 = json.loads(resp2.get_data(as_text=True))
        assert data2["is_favorited"] is False
        assert data2["count"] == 0
