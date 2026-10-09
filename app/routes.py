from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models.ticket import Ticket
from app.services.ticket_query_service import filtered_ticket_query, normalize_filters, paginate_tickets

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/health")
def health():
    return {"status": "ok"}, 200


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    if current_user.role == "agent":
        return redirect(url_for("agent.dashboard"))

    filters = normalize_filters(request.args)
    pagination = paginate_tickets(
        filtered_ticket_query(filters, customer_id=current_user.id),
        request.args.get("page", 1, type=int),
        filters["per_page"],
    )
    customer_query = Ticket.query.filter_by(customer_id=current_user.id)
    stats = {
        "total": customer_query.count(),
        "open": customer_query.filter_by(status="open").count(),
        "in_progress": customer_query.filter_by(status="in_progress").count(),
        "resolved": customer_query.filter_by(status="resolved").count(),
    }

    return render_template(
        "customer/dashboard.html",
        tickets=pagination.items,
        pagination=pagination,
        filters=filters,
        stats=stats,
    )
