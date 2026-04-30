"""Integration tests for auth blueprint routes."""

from app.services.user_service import create_user


class TestAuthRoutes:
    """Test auth routes: register, login, logout."""

    def test_get_register_page(self, client):
        """GET /auth/register returns 200 with registration form."""
        resp = client.get("/auth/register")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "用户注册" in html

    def test_get_login_page(self, client):
        """GET /auth/login returns 200 with login form."""
        resp = client.get("/auth/login")
        assert resp.status_code == 200
        assert "用户登录" in resp.get_data(as_text=True)

    def test_register_success(self, client):
        """POST /auth/register creates user and redirects to login."""
        resp = client.post("/auth/register", data={
            "username": "newstudent",
            "student_id": "20240099",
            "email": "new@campus.edu.cn",
            "password": "StrongPass1",
            "confirm_password": "StrongPass1",
            "campus": "广州新港校区",
                    }, follow_redirects=True)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "注册成功" in html
        assert "用户登录" in html  # Redirected to login page

    def test_register_duplicate_username(self, client, app):
        """Duplicate username triggers validation error."""
        with app.app_context():
            create_user("dupuser", "20001", "dup@campus.edu.cn", "Pass1234", "广州新港校区")

        resp = client.post("/auth/register", data={
            "username": "dupuser",
            "student_id": "20002",
            "email": "another@campus.edu.cn",
            "password": "Pass1234",
            "confirm_password": "Pass1234",
            "campus": "广州新港校区",
                    })
        assert resp.status_code == 200
        assert "已被注册" in resp.get_data(as_text=True)

    def test_register_duplicate_email(self, client, app):
        """Duplicate email triggers validation error."""
        with app.app_context():
            create_user("user1", "20010", "same@campus.edu.cn", "Pass1234", "广州新港校区")

        resp = client.post("/auth/register", data={
            "username": "user2",
            "student_id": "20011",
            "email": "same@campus.edu.cn",
            "password": "Pass1234",
            "confirm_password": "Pass1234",
            "campus": "广州新港校区",
                    })
        assert "已被注册" in resp.get_data(as_text=True)

    def test_register_password_mismatch(self, client):
        """Password confirmation mismatch triggers error."""
        resp = client.post("/auth/register", data={
            "username": "testuser1",
            "student_id": "20020",
            "email": "t1@campus.edu.cn",
            "password": "Pass1234",
            "confirm_password": "Different456",
            "campus": "广州新港校区",
                    })
        assert "不一致" in resp.get_data(as_text=True)

    def test_login_success(self, client, app):
        """Successful login redirects to index with welcome message."""
        with app.app_context():
            create_user("loginuser", "30001", "login@campus.edu.cn", "Pass1234", "广州新港校区")

        resp = client.post("/auth/login", data={
            "login_id": "loginuser",
            "password": "Pass1234",
        }, follow_redirects=True)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "登录成功" in html

    def test_login_by_email(self, client, app):
        """Login with email instead of username works."""
        with app.app_context():
            create_user("emailuser", "30002", "myemail@campus.edu.cn", "Pass1234", "广州新港校区")

        resp = client.post("/auth/login", data={
            "login_id": "myemail@campus.edu.cn",
            "password": "Pass1234",
        }, follow_redirects=True)
        assert "登录成功" in resp.get_data(as_text=True)

    def test_login_wrong_password(self, client, app):
        """Wrong password returns error message."""
        with app.app_context():
            create_user("failuser", "30003", "fail@campus.edu.cn", "Pass1234", "广州新港校区")

        resp = client.post("/auth/login", data={
            "login_id": "failuser",
            "password": "WrongPassword",
        })
        assert resp.status_code == 200
        assert "错误" in resp.get_data(as_text=True)

    def test_login_nonexistent_user(self, client):
        """Login with nonexistent credentials returns error."""
        resp = client.post("/auth/login", data={
            "login_id": "nobody",
            "password": "nopass",
        })
        assert "错误" in resp.get_data(as_text=True)

    def test_logout(self, client, app):
        """Logout clears session and redirects to index."""
        with app.app_context():
            create_user("logoutuser", "30004", "logout@campus.edu.cn", "Pass1234", "广州新港校区")

        client.post("/auth/login", data={
            "login_id": "logoutuser",
            "password": "Pass1234",
        })

        resp = client.get("/auth/logout", follow_redirects=True)
        assert resp.status_code == 200
        assert "退出登录" in resp.get_data(as_text=True)

    def test_protected_page_redirects_anonymous(self, client):
        """Anonymous user accessing protected page is redirected to login."""
        resp = client.get("/user/profile", follow_redirects=True)
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "请先登录" in html

    def test_already_logged_in_redirects_login_page(self, client, app):
        """Logged-in user visiting login page is redirected."""
        with app.app_context():
            create_user("rediruser", "30005", "redir@campus.edu.cn", "Pass1234", "广州新港校区")

        client.post("/auth/login", data={
            "login_id": "rediruser",
            "password": "Pass1234",
        })

        resp = client.get("/auth/login", follow_redirects=True)
        html = resp.get_data(as_text=True)
        # Should be on index page, not login page
        assert "用户登录" not in html
