from flask import Flask

from app.extensions import db, login_manager, migrate


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object("config.settings.Config")

    if test_config:
        app.config.update(test_config)
        if app.config.get("TESTING") and "CSRF_PROTECTION_ENABLED" not in test_config:
            app.config["CSRF_PROTECTION_ENABLED"] = False

    if not app.config.get("TESTING"):
        from config.settings import Config
        Config.validate()

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.security import csrf_token, validate_csrf_request

    app.before_request(validate_csrf_request)

    @app.context_processor
    def inject_security_helpers():
        from flask_login import current_user
        unread_notifications = 0
        if current_user.is_authenticated:
            from app.models.notification import Notification
            unread_notifications = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {"csrf_token": csrf_token, "unread_notifications": unread_notifications}

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.tickets.routes import tickets_bp
    app.register_blueprint(tickets_bp)

    from app.agent.routes import agent_bp
    app.register_blueprint(agent_bp)

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from app.notifications import notifications_bp
    app.register_blueprint(notifications_bp)

    from app.knowledge import knowledge_bp
    app.register_blueprint(knowledge_bp)

    from app.api import api_v1_bp
    app.register_blueprint(api_v1_bp)

    @app.cli.command("create-api-token")
    def create_api_token_command():
        """Create an API token. Usage: flask create-api-token --email user@example.com"""
        import click
        from app.models.api_token import ApiToken
        from app.models.user import User

        email = click.prompt("Email").strip().lower()
        name = click.prompt("Token name", default="Personal API token").strip()
        user = User.query.filter_by(email=email).first()
        if not user:
            raise click.ClickException("No user exists with that email.")
        token, raw_token = ApiToken.issue(user.id, name)
        db.session.add(token)
        db.session.commit()
        click.echo("Copy this token now. It will not be shown again:")
        click.echo(raw_token)

    @app.cli.command("seed-demo-data")
    def seed_demo_data_command():
        """Create fictional local demo accounts and tickets."""
        from app.services.seed_service import seed_development_data
        import click
        if app.config["APP_ENV"] == "production":
            raise click.ClickException("Demo data cannot be seeded in production.")
        created = seed_development_data()
        click.echo(f"Created {created} demo tickets. Password for demo accounts: Password123")

    @app.cli.command("purge-demo-data")
    def purge_demo_data_command():
        """Remove only fictional .test demo accounts and their sample records."""
        from app.services.seed_service import purge_development_data
        import click
        accounts, tickets = purge_development_data()
        click.echo(f"Removed {accounts} demo accounts and {tickets} demo tickets.")

    from app.errors import register_error_handlers
    register_error_handlers(app)

    return app
