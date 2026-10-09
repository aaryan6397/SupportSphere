from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.admin import admin_bp
from app.decorators import admin_required
from app.extensions import db
from app.models.feedback import TicketFeedback
from app.models.ticket import Ticket
from app.models.user import User
from app.services.notification_service import create_notification
from app.services.audit_service import log_event
from app.services.ticket_query_service import filtered_ticket_query, normalize_filters, paginate_tickets
from app.services.sla_service import ticket_sla_status
from app.services.workload_service import build_agent_workload
from app.validators import password_error, validate_email


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    filters = normalize_filters(request.args)
    pagination = paginate_tickets(
        filtered_ticket_query(filters),
        request.args.get("page", 1, type=int),
        filters["per_page"],
    )

    agents = User.query.filter_by(
        role="agent",
        is_active_account=True
    ).order_by(User.name).all()

    customers_count = User.query.filter_by(
        role="customer"
    ).count()

    active_tickets = Ticket.query.filter(
        Ticket.status.notin_(["resolved", "closed"])
    ).all()
    sla_at_risk = sum(ticket_sla_status(ticket) == "AT_RISK" for ticket in active_tickets)
    sla_breached = sum(ticket_sla_status(ticket) == "BREACHED" for ticket in active_tickets)

    stats = {
        "total": Ticket.query.count(),
        "open": Ticket.query.filter_by(status="open").count(),
        "in_progress": Ticket.query.filter_by(
            status="in_progress"
        ).count(),
        "resolved": Ticket.query.filter_by(
            status="resolved"
        ).count(),
        "sla_at_risk": sla_at_risk,
        "sla_breached": sla_breached,
        "agents": len(agents),
        "customers": customers_count
    }

    category_rows = db.session.query(
        Ticket.category,
        func.count(Ticket.id)
    ).group_by(
        Ticket.category
    ).order_by(
        func.count(Ticket.id).desc()
    ).all()

    category_stats = []

    for category, count in category_rows:
        percentage = 0

        if stats["total"] > 0:
            percentage = round(
                (count / stats["total"]) * 100
            )

        category_stats.append({
            "category": category,
            "count": count,
            "percentage": percentage
        })

    average_rating = db.session.query(
        func.avg(TicketFeedback.rating)
    ).scalar()

    feedback_count = TicketFeedback.query.count()

    if average_rating:
        average_rating = round(float(average_rating), 1)
    else:
        average_rating = 0

    assigned_tickets = Ticket.query.filter(
        Ticket.assigned_agent_id.isnot(None)
    ).all()
    agent_workload, recommended_agent = build_agent_workload(agents, assigned_tickets)

    return render_template(
        "admin/dashboard.html",
        tickets=pagination.items,
        pagination=pagination,
        filters=filters,
        agents=agents,
        stats=stats,
        category_stats=category_stats,
        average_rating=average_rating,
        feedback_count=feedback_count,
        agent_workload=agent_workload,
        recommended_agent=recommended_agent,
    )


@admin_bp.route("/agents/create", methods=["POST"])
@login_required
@admin_required
def create_agent():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        flash("All agent fields are required.", "error")

    elif len(name) > 120:
        flash("Agent name must be 120 characters or fewer.", "error")

    elif not validate_email(email):
        flash("Please enter a valid agent email address.", "error")

    elif password_error(password):
        flash(password_error(password), "error")

    elif User.query.filter_by(email=email).first():
        flash(
            "An account already exists with this email.",
            "error"
        )

    else:
        agent = User(
            name=name,
            email=email,
            role="agent"
        )

        agent.set_password(password)

        db.session.add(agent)
        db.session.flush()
        log_event("agent_created", f"Created agent account for {agent.email}.", current_user.id, "user", agent.id)
        db.session.commit()

        flash(
            f"Agent {agent.name} was created successfully.",
            "success"
        )

    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/tickets/<int:ticket_id>/assign", methods=["POST"])
@login_required
@admin_required
def assign_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)

    agent_id = request.form.get("agent_id", type=int)

    agent = db.session.get(User, agent_id)

    if not agent or agent.role != "agent":
        flash("Please select a valid support agent.", "error")

    else:
        ticket.assigned_agent_id = agent.id

        if ticket.status == "open":
            ticket.status = "assigned"

        ticket_link = url_for("tickets.ticket_detail", ticket_id=ticket.id)
        create_notification(
            agent.id,
            "Ticket assigned to you",
            f"{ticket.ticket_code}: {ticket.subject}",
            ticket_link,
        )
        create_notification(
            ticket.customer_id,
            "Your ticket has been assigned",
            f"{ticket.ticket_code} is now assigned to {agent.name}.",
            ticket_link,
        )

        log_event("ticket_assigned", f"Assigned {ticket.ticket_code} to {agent.name}.", current_user.id, "ticket", ticket.id)

        db.session.commit()

        flash(
            f"{ticket.ticket_code} assigned to {agent.name}.",
            "success"
        )

    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/activity")
@login_required
@admin_required
def activity_logs():
    from app.models.audit_log import AuditLog

    logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).all()

    return render_template(
        "admin/activity_logs.html",
        logs=logs
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:user_id>/active", methods=["POST"])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own administrator account.", "error")
    elif user.role == "admin":
        flash("Administrator account status cannot be changed here.", "error")
    else:
        user.is_active_account = not user.is_active_account
        log_event(
            "user_activation_changed",
            f"{'Activated' if user.is_active_account else 'Deactivated'} {user.email}.",
            current_user.id, "user", user.id,
        )
        db.session.commit()
        flash(f"Account {'activated' if user.is_active_account else 'deactivated'}.", "success")
    return redirect(url_for("admin.users"))
