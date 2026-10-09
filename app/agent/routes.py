from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.agent import agent_bp
from app.decorators import agent_required
from app.extensions import db
from app.models.ticket import Ticket
from app.services.ticket_service import transition_ticket
from app.services.ticket_query_service import filtered_ticket_query, normalize_filters, paginate_tickets
from app.services.notification_service import create_notification
from app.services.audit_service import log_event


@agent_bp.route("/dashboard")
@login_required
@agent_required
def dashboard():
    filters = normalize_filters(request.args)
    pagination = paginate_tickets(
        filtered_ticket_query(filters, agent_id=current_user.id),
        request.args.get("page", 1, type=int),
        filters["per_page"],
    )
    agent_query = Ticket.query.filter_by(assigned_agent_id=current_user.id)
    stats = {
        "total": agent_query.count(),
        "assigned": agent_query.filter_by(status="assigned").count(),
        "in_progress": agent_query.filter_by(status="in_progress").count(),
        "resolved": agent_query.filter_by(status="resolved").count(),
    }

    return render_template(
        "agent/dashboard.html",
        tickets=pagination.items,
        pagination=pagination,
        filters=filters,
        stats=stats,
    )


@agent_bp.route("/tickets/<int:ticket_id>/status", methods=["POST"])
@login_required
@agent_required
def update_ticket_status(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    if ticket.assigned_agent_id != current_user.id:
        abort(403)

    status = request.form.get("status", "").strip()

    success, message = transition_ticket(ticket, status)

    if success:
        create_notification(
            ticket.customer_id,
            "Ticket status updated",
            f"{ticket.ticket_code} is now {ticket.status.replace('_', ' ')}.",
            url_for("tickets.ticket_detail", ticket_id=ticket.id),
        )
        log_event("ticket_status_updated", f"Changed {ticket.ticket_code} status to {ticket.status}.", current_user.id, "ticket", ticket.id)
        db.session.commit()
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(
        url_for("tickets.ticket_detail", ticket_id=ticket.id)
    )
