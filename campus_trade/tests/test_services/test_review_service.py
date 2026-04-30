"""Unit tests for review service layer."""

import pytest
from app.services.user_service import create_user
from app.services.product_service import create_product
from app.services.order_service import create_order, confirm_order, complete_order
from app.services.review_service import create_review, has_reviewed, get_user_reviews
from app.extensions import db
from app.models.category import Category
from app.models.user import User


class TestReviewService:
    """Test review service business logic."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        with app.app_context():
            db.create_all()
            cat = Category(name="电子", sort_order=1)
            db.session.add(cat)
            db.session.commit()
            self.cat_id = cat.id
            seller = create_user("rvseller", "RV01", "rvs@t.com", "Pass1234", "广州新港校区")
            buyer = create_user("rvbuyer", "RV02", "rvb@t.com", "Pass1234", "广州琶洲校区")
            self.seller_id = seller.id
            self.buyer_id = buyer.id

    def test_create_review(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "评价商品", "描述十个字测试", 50.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            seller = db.session.get(User, self.seller_id)
            confirm_order(order, seller)
            complete_order(order, seller)

            review, error = create_review(order.id, self.buyer_id, 5, "很好")
            assert error is None
            assert review.rating == 5
            assert review.content == "很好"

    def test_cannot_review_uncompleted_order(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "未完成", "描述十个字测试", 30.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            review, error = create_review(order.id, self.buyer_id, 4)
            assert review is None
            assert "已完成" in error

    def test_cannot_review_twice(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "重复评价", "描述十个字测试", 40.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            seller = db.session.get(User, self.seller_id)
            confirm_order(order, seller)
            complete_order(order, seller)
            create_review(order.id, self.buyer_id, 5)
            assert has_reviewed(order.id, self.buyer_id) is True
            review2, error = create_review(order.id, self.buyer_id, 3)
            assert review2 is None
            assert "已经评价" in error

    def test_review_updates_credit_score(self, app):
        with app.app_context():
            p = create_product(self.seller_id, "信用分", "描述十个字测试", 60.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            seller = db.session.get(User, self.seller_id)
            confirm_order(order, seller)
            complete_order(order, seller)
            # Buyer reviews seller with 5 stars
            create_review(order.id, self.buyer_id, 5)
            # Seller credit should be high
            seller = db.session.get(User, self.seller_id)
            assert seller.credit_score > 50


class TestReviewRoutes:
    """Test review route endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        with app.app_context():
            db.create_all()
            cat = Category(name="电子", sort_order=1)
            db.session.add(cat)
            db.session.commit()
            self.cat_id = cat.id
            seller = create_user("rvseller2", "RV03", "rvs2@t.com", "Pass1234", "广州新港校区")
            buyer = create_user("rvbuyer2", "RV04", "rvb2@t.com", "Pass1234", "广州琶洲校区")
            self.seller_id = seller.id
            self.buyer_id = buyer.id

    def test_review_page_for_completed_order(self, client, app):
        with app.app_context():
            p = create_product(self.seller_id, "路由评价", "描述十个字测试", 20.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            seller = db.session.get(User, self.seller_id)
            confirm_order(order, seller)
            complete_order(order, seller)
            oid = order.id

        client.post("/auth/login", data={"login_id": "rvbuyer2", "password": "Pass1234"})
        resp = client.get(f"/orders/{oid}/review")
        assert resp.status_code == 200
        assert "评价" in resp.get_data(as_text=True)

    def test_submit_review(self, client, app):
        with app.app_context():
            p = create_product(self.seller_id, "提交评价商品", "描述十个字测试", 20.00, self.cat_id, "广州新港校区")
            order, _ = create_order(self.buyer_id, p.id)
            seller = db.session.get(User, self.seller_id)
            confirm_order(order, seller)
            complete_order(order, seller)
            oid = order.id

        client.post("/auth/login", data={"login_id": "rvbuyer2", "password": "Pass1234"})
        resp = client.post(f"/orders/{oid}/review", data={
            "rating": "5",
            "content": "非常满意",
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        assert "评价提交成功" in html
