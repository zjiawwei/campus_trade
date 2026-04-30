from functools import wraps
from flask import abort
from flask_login import current_user
from app.utils.constants import ROLE_ADMIN


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
