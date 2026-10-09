from functools import wraps

from flask import abort
from flask_login import current_user


def roles_required(*allowed_roles):
    """Restrict a view to one or more SupportSphere roles."""
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped_view
    return decorator


def admin_required(view):
    return roles_required("admin")(view)


def agent_required(view):
    return roles_required("agent")(view)


def customer_required(view):
    return roles_required("customer")(view)
