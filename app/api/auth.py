from datetime import datetime
from functools import wraps
from hashlib import sha256
import hmac

from flask import g, jsonify, request

from app.extensions import db
from app.models.api_token import ApiToken


def api_token_required(view):
    """Authenticate API calls using a hashed Bearer token stored in the database."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, raw_token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not raw_token.startswith("ss_"):
            return jsonify(error={"code": "authentication_required", "message": "Use a Bearer API token."}), 401

        try:
            prefix = raw_token.split(".", 1)[0].removeprefix("ss_")
        except IndexError:
            return jsonify(error={"code": "invalid_token", "message": "Invalid API token."}), 401

        token = ApiToken.query.filter_by(token_prefix=prefix, is_revoked=False).first()
        digest = sha256(raw_token.encode()).hexdigest()
        if not token or not hmac.compare_digest(token.token_hash, digest) or not token.user.is_active_account:
            return jsonify(error={"code": "invalid_token", "message": "Invalid or revoked API token."}), 401

        token.last_used_at = datetime.utcnow()
        db.session.commit()
        g.api_user = token.user
        return view(*args, **kwargs)
    return wrapped_view
