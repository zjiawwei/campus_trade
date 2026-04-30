from app.extensions import db
from app.models.user import User


def create_user(username, student_id, password, campus, **kwargs):
    """Create a new user with hashed password. Returns the User object."""
    user = User(
        username=username,
        student_id=student_id,
        campus=campus,
        **kwargs,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(username, password):
    """Authenticate a user by username. Returns User or None."""
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        if not user.is_active:
            return None
        return user
    return None


def get_user_by_id(user_id):
    """Get a user by primary key. Returns User or None."""
    return db.session.get(User, user_id)


def get_user_by_username(username):
    """Get a user by username. Returns User or None."""
    return User.query.filter_by(username=username).first()


def get_user_by_student_id(student_id):
    """Get a user by student ID. Returns User or None."""
    return User.query.filter_by(student_id=student_id).first()


def update_profile(user, **kwargs):
    """Update user profile fields. Only updates provided non-None values."""
    updatable_fields = {"real_name", "phone", "campus", "avatar"}
    for field, value in kwargs.items():
        if field in updatable_fields and value is not None:
            setattr(user, field, value)
    db.session.commit()
    return user


def change_password(user, old_password, new_password):
    """Change password for a user. Returns True on success, false on failure."""
    if not user.check_password(old_password):
        return False
    user.set_password(new_password)
    db.session.commit()
    return True
