import secrets

from flask import abort, current_app, request, session


def csrf_token():
    """Return the session-bound token used by every state-changing form."""
    token = session.get("_csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf_request():
    """Reject unsafe browser requests that do not contain a valid CSRF token."""
    if not current_app.config.get("CSRF_PROTECTION_ENABLED", True):
        return

    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return

    if request.endpoint and request.endpoint.startswith("api_v1."):
        return

    expected_token = session.get("_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")

    if not expected_token or not submitted_token:
        abort(400, description="Your form session has expired. Please try again.")

    if not secrets.compare_digest(expected_token, submitted_token):
        abort(400, description="Invalid form security token.")
