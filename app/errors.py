from flask import render_template


def register_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template(
            "errors/403.html"
        ), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            "errors/404.html"
        ), 404

    @app.errorhandler(413)
    def file_too_large_error(error):
        return render_template(
            "errors/413.html"
        ), 413

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template(
            "errors/generic.html",
            error_code=400,
            title="Request could not be processed",
            message=getattr(error, "description", "Please try again."),
        ), 400

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return render_template(
            "errors/generic.html",
            error_code=405,
            title="Action not allowed",
            message="This action is not available from this page.",
        ), 405

    @app.errorhandler(500)
    def server_error(error):
        return render_template(
            "errors/generic.html",
            error_code=500,
            title="Something went wrong",
            message="Our team has been notified. Please try again in a moment.",
        ), 500

    @app.errorhandler(429)
    def rate_limit_error(error):
        return render_template(
            "errors/generic.html",
            error_code=429,
            title="Too many requests",
            message=getattr(error, "description", "Please wait before trying again."),
        ), 429
