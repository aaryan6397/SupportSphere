import re


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_email(email):
    return bool(EMAIL_PATTERN.fullmatch(email))


def password_error(password):
    """Return a user-friendly strength error, or None for an acceptable password."""
    if len(password) < 8:
        return "Password must contain at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must include at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must include at least one number."
    return None
