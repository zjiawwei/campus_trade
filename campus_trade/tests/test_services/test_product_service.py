"""Unit tests for product service layer."""

import pytest
from app.services.user_service import create_user
from app.services.product_service import (
    create_product,
    update_product,
    withdraw_product,
    delete_product,
    get_product,
    search_products,
    toggle_favorite,
    is_favorited,
)
from app.extensions import db
from app.models.category import Category


class TestProductService:
    """Test product service business logic."""

    @pytest.fixture(autouse=True)
    def setup(self, app):
        with app.app_context():
            seller = create_user(
                "prodseller", "P001", "Pass1234", "广州新港校区"
            )
            cat = Category(name="电子产品", icon="bi-laptop", sort_order=2)
            db.session.add(cat)
            db.session.commit()
            self.seller_id = seller.id
            self.category_id = cat.id

    def _make_product(self, **kwargs):
        defaults = {
            "seller_id": self.seller_id,
            "title": "测试商品",
            "description": "这是一个测试商品的描述信息",
            "price": 10.00,
            "category_id": self.category_id,
            "campus": "广州新港校区",
        }
        defaults.update(kwargs)
        return create_product(**defaults)

    def test_create_product(self, app):
        with app.app_context():
            product = self._make_product(
                title="测试商品", price=99.00, original_price=199.00,
                condition="like_new",
            )
            assert product.id is not None
            assert product.title == "测试商品"
            assert float(product.price) == 99.00
            assert product.status == "active"

    def test_search_by_keyword(self, app):
        with app.app_context():
            self._make_product(title="Python教程", description="编程入门好书")
            self._make_product(title="Java编程", description="经典Java书籍")

            results = search_products(keyword="Python")
            assert len(results.items) >= 1
            assert results.items[0].title == "Python教程"

            results2 = search_products(keyword="编程")
            assert len(results2.items) >= 2

    def test_search_by_category(self, app):
        with app.app_context():
            self._make_product(title="商品A")
            results = search_products(category_id=self.category_id)
            assert len(results.items) >= 1
            results2 = search_products(category_id=99999)
            assert len(results2.items) == 0

    def test_update_product(self, app):
        with app.app_context():
            p = self._make_product(title="旧标题")
            updated = update_product(p, title="新标题", price=20.00)
            assert updated.title == "新标题"
            assert float(updated.price) == 20.00

    def test_withdraw_product(self, app):
        with app.app_context():
            p = self._make_product(title="下架测试")
            assert p.status == "active"
            withdraw_product(p)
            assert p.status == "withdrawn"

    def test_delete_product(self, app):
        with app.app_context():
            p = self._make_product(title="删除测试")
            pid = p.id
            delete_product(p)
            assert get_product(pid) is None

    def test_increment_view_count(self, app):
        from app.services.product_service import increment_view_count
        with app.app_context():
            p = self._make_product(title="浏览量")
            assert p.view_count == 0
            increment_view_count(p)
            assert p.view_count == 1

    def test_toggle_favorite(self, app):
        with app.app_context():
            p = self._make_product(title="收藏测试")
            is_fav, count = toggle_favorite(self.seller_id, p.id)
            assert is_fav is True
            assert count == 1
            assert is_favorited(self.seller_id, p.id) is True

            is_fav2, count2 = toggle_favorite(self.seller_id, p.id)
            assert is_fav2 is False
            assert count2 == 0

    def test_is_favorited_nonexistent(self, app):
        with app.app_context():
            assert is_favorited(99999, 99999) is False


class TestProductForm:
    """Test product form validation."""

    def test_valid_form(self, app):
        from app.blueprints.product.forms import ProductForm
        from werkzeug.datastructures import ImmutableMultiDict
        with app.app_context():
            db.create_all()
            cat = Category(name="测试分类", sort_order=99)
            db.session.add(cat)
            db.session.commit()

            form = ProductForm(formdata=ImmutableMultiDict({
                "title": "测试商品标题",
                "description": "这是超过十个字的商品详细描述",
                "price": "50.00",
                "condition": "used",
                "category_id": str(cat.id),
                "campus": "广州新港校区",
            }))
            form.category_id.choices = [(cat.id, cat.name)]
            assert form.validate() is True

    def test_invalid_form(self, app):
        from app.blueprints.product.forms import ProductForm
        with app.app_context():
            form = ProductForm(data={})
            assert form.validate() is False
            assert "title" in form.errors
            assert "description" in form.errors
            assert "price" in form.errors
