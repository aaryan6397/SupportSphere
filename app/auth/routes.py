from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from flask import abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import auth_bp
from app.extensions import db
from app.models.user import User
from app.validators import password_error, validate_email
from app.services.email_service import send_password_reset_email
from app.services.rate_limit_service import is_rate_limited, record_rate_limit_event
from app.services.audit_service import log_event


def password_reset_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_reset_token(user):
    return password_reset_serializer().dumps(
        {"user_id": user.id, "version": user.password_reset_version},
        salt="supportsphere-password-reset",
    )


def load_reset_user(token):
    try:
        data = password_reset_serializer().loads(
            token,
            salt="supportsphere-password-reset",
            max_age=current_app.config["PASSWORD_RESET_MAX_AGE"],
        )
    except (BadSignature, SignatureExpired):
        return None
    user = db.session.get(User, data.get("user_id"))
    if not user or user.password_reset_version != data.get("version"):
        return None
    return user


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")

        elif len(name) > 120:
            flash("Name must be 120 characters or fewer.", "error")

        elif not validate_email(email):
            flash("Please enter a valid email address.", "error")

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        elif password_error(password):
            flash(password_error(password), "error")

        elif User.query.filter_by(email=email).first():
            flash("An account already exists with this email.", "error")

        else:
            user = User(
                name=name,
                email=email,
                role="customer"
            )

            user.set_password(password)

            db.session.add(user)
            db.session.flush()
            log_event("user_registered", "Registered a customer account.", user.id, "user", user.id)
            db.session.commit()

            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        rate_key = f"{email}|{request.remote_addr or 'unknown'}"

        if is_rate_limited(
            "login_failure", rate_key, current_app.config["LOGIN_RATE_LIMIT"],
            current_app.config["RATE_LIMIT_WINDOW_SECONDS"],
        ):
            abort(429, description="Too many login attempts. Please try again in 15 minutes.")

        if not validate_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            record_rate_limit_event("login_failure", rate_key)
            flash("Invalid email or password.", "error")

        elif not user.is_active_account:
            flash("Your account is inactive. Contact support.", "error")

        else:
            login_user(user, remember=remember)
            log_event("user_logged_in", "Logged in to SupportSphere.", user.id, "user", user.id)
            db.session.commit()

            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("main.home"))

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    log_event("user_logged_out", "Logged out of SupportSphere.", current_user.id, "user", current_user.id)
    db.session.commit()
    logout_user()

    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        rate_key = f"{email}|{request.remote_addr or 'unknown'}"
        if is_rate_limited(
            "password_reset", rate_key, current_app.config["PASSWORD_RESET_RATE_LIMIT"],
            current_app.config["RATE_LIMIT_WINDOW_SECONDS"],
        ):
            abort(429, description="Too many reset requests. Please try again in 15 minutes.")
        record_rate_limit_event("password_reset", rate_key)
        user = User.query.filter_by(email=email).first() if validate_email(email) else None
        if user and user.is_active_account:
            reset_url = url_for("auth.reset_password", token=generate_reset_token(user), _external=True)
            try:
                send_password_reset_email(user.email, reset_url)
            except Exception:
                current_app.logger.exception("Password reset email delivery failed for user id %s", user.id)
        flash("If an active account matches that email, a password-reset link has been sent.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    user = load_reset_user(token)
    if not user:
        flash("This password-reset link is invalid or has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if password != confirm_password:
            flash("Passwords do not match.", "error")
        elif password_error(password):
            flash(password_error(password), "error")
        else:
            user.set_password(password)
            user.password_reset_version += 1
            db.session.commit()
            flash("Password updated. You can now log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", token=token)
