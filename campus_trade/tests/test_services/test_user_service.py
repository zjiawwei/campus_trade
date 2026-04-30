"""Unit tests for user service layer."""

import pytest
from app.services.user_service import (
    create_user,
    authenticate_user,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    get_user_by_student_id,
    update_profile,
    change_password,
)
from app.extensions import db
from app.models.user import User
from sqlalchemy.exc import IntegrityError


class TestUserService:
    """Test user service business logic."""

    def test_create_user(self, app):
        """create_user returns a User with hashed password."""
        with app.app_context():
            user = create_user("svcuser", "S10001", "svc@test.edu.cn", "Test1234", "广州新港校区")
            assert user.id is not None
            assert user.username == "svcuser"
            assert user.password_hash != "Test1234"
            assert len(user.password_hash) > 50
            assert user.check_password("Test1234")

    def test_create_user_duplicate_username_raises(self, app):
        """Creating user with duplicate username fails."""
        with app.app_context():
            create_user("unique1", "S20001", "u1@test.edu.cn", "Pass1234", "广州新港校区")
            with pytest.raises(IntegrityError):
                create_user("unique1", "S20002", "u2@test.edu.cn", "Pass1234", "广州新港校区")

    def test_authenticate_by_username(self, app):
        """Authenticate succeeds with correct username + password."""
        with app.app_context():
            create_user("authuser", "S30001", "auth@test.edu.cn", "Secret123", "广州新港校区")
            user = authenticate_user("authuser", "Secret123")
            assert user is not None
            assert user.username == "authuser"

    def test_authenticate_by_email(self, app):
        """Authenticate succeeds with email + password."""
        with app.app_context():
            create_user("emailauth", "S30002", "em@test.edu.cn", "Secret123", "广州新港校区")
            user = authenticate_user("em@test.edu.cn", "Secret123")
            assert user is not None
            assert user.username == "emailauth"

    def test_authenticate_wrong_password(self, app):
        """Authenticate returns None for wrong password."""
        with app.app_context():
            create_user("wrongpw", "S40001", "wp@test.edu.cn", "Correct1", "广州新港校区")
            user = authenticate_user("wrongpw", "Wrong1")
            assert user is None

    def test_authenticate_nonexistent(self, app):
        """Authenticate returns None for nonexistent user."""
        with app.app_context():
            user = authenticate_user("nobody", "nopass")
            assert user is None

    def test_get_user_by_id(self, app):
        """get_user_by_id retrieves correct user."""
        with app.app_context():
            created = create_user("byid", "S50001", "byid@test.edu.cn", "Pass1234", "广州琶洲校区")
            fetched = get_user_by_id(created.id)
            assert fetched is not None
            assert fetched.username == "byid"

    def test_get_user_by_id_nonexistent(self, app):
        """get_user_by_id returns None for nonexistent id."""
        with app.app_context():
            assert get_user_by_id(99999) is None

    def test_get_user_by_username(self, app):
        """get_user_by_username finds correct user."""
        with app.app_context():
            create_user("findme", "S60001", "find@test.edu.cn", "Pass1234", "广州新港校区")
            assert get_user_by_username("findme") is not None
            assert get_user_by_username("nonexistent") is None

    def test_get_user_by_email(self, app):
        """get_user_by_email finds correct user."""
        with app.app_context():
            create_user("emailfind", "S70001", "efind@test.edu.cn", "Pass1234", "广州新港校区")
            assert get_user_by_email("efind@test.edu.cn") is not None
            assert get_user_by_email("no@test.edu.cn") is None

    def test_get_user_by_student_id(self, app):
        """get_user_by_student_id finds correct user."""
        with app.app_context():
            create_user("stufind", "S80001", "stu@test.edu.cn", "Pass1234", "广州新港校区")
            assert get_user_by_student_id("S80001") is not None
            assert get_user_by_student_id("X99999") is None

    def test_update_profile(self, app):
        """update_profile updates allowed fields only."""
        with app.app_context():
            user = create_user("updateu", "S90001", "up@test.edu.cn", "Pass1234", "广州新港校区")
            updated = update_profile(user, real_name="新名字", phone="13800138000", campus="广州琶洲校区")
            assert updated.real_name == "新名字"
            assert updated.phone == "13800138000"
            assert updated.campus == "广州琶洲校区"

    def test_update_profile_ignores_non_updatable(self, app):
        """update_profile ignores fields that should not be changed."""
        with app.app_context():
            user = create_user("safeu", "S91001", "safe@test.edu.cn", "Pass1234", "广州新港校区")
            original_email = user.email
            updated = update_profile(user, email="hacked@evil.com", phone="13900000000")
            assert updated.email == original_email

    def test_change_password_success(self, app):
        """change_password updates the password hash."""
        with app.app_context():
            user = create_user("chpwd", "SA0001", "cp@test.edu.cn", "OldPass1", "广州新港校区")
            result = change_password(user, "OldPass1", "NewPass2")
            assert result is True
            assert user.check_password("NewPass2")
            assert not user.check_password("OldPass1")

    def test_change_password_wrong_old(self, app):
        """change_password fails with wrong old password."""
        with app.app_context():
            user = create_user("chpwd2", "SA0002", "cp2@test.edu.cn", "OldPass1", "广州新港校区")
            result = change_password(user, "WrongOld", "NewPass2")
            assert result is False
            assert user.check_password("OldPass1")
