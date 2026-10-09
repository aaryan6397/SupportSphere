from datetime import datetime

from flask import g, jsonify, request, url_for

from app.api import api_v1_bp
from app.api.auth import api_token_required
from app.extensions import db
from app.models.comment import TicketComment
from app.models.ticket import Ticket, calculate_sla_due_at
from app.services.ticket_query_service import filtered_ticket_query, normalize_filters, paginate_tickets
from app.services.ticket_service import transition_ticket


def error_response(code, message, status=400):
    return jsonify(error={"code": code, "message": message}), status


@api_v1_bp.errorhandler(404)
def api_not_found(error):
    return error_response("not_found", "The requested API resource was not found.", 404)


@api_v1_bp.errorhandler(405)
def api_method_not_allowed(error):
    return error_response("method_not_allowed", "This HTTP method is not allowed for the resource.", 405)


def ticket_access_allowed(user, ticket):
    return (
        user.role == "admin"
        or (user.role == "customer" and ticket.customer_id == user.id)
        or (user.role == "agent" and ticket.assigned_agent_id == user.id)
    )


def ticket_payload(ticket):
    return {
        "id": ticket.id,
        "code": ticket.ticket_code,
        "subject": ticket.subject,
        "category": ticket.category,
        "priority": ticket.priority,
        "description": ticket.description,
        "status": ticket.status,
        "customer_id": ticket.customer_id,
        "assigned_agent_id": ticket.assigned_agent_id,
        "sla_due_at": ticket.sla_due_at.isoformat() if ticket.sla_due_at else None,
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat(),
    }


@api_v1_bp.get("/tickets")
@api_token_required
def list_tickets():
    filters = normalize_filters(request.args)
    user = g.api_user
    scope = {"customer_id": user.id} if user.role == "customer" else {}
    if user.role == "agent":
        scope = {"agent_id": user.id}
    pagination = paginate_tickets(
        filtered_ticket_query(filters, **scope),
        request.args.get("page", 1, type=int),
        filters["per_page"],
    )
    return jsonify({
        "data": [ticket_payload(ticket) for ticket in pagination.items],
        "pagination": {
            "page": pagination.page, "per_page": pagination.per_page,
            "total": pagination.total, "pages": pagination.pages,
        },
    })


@api_v1_bp.post("/tickets")
@api_token_required
def create_ticket():
    if g.api_user.role != "customer":
        return error_response("forbidden", "Only customers can create tickets.", 403)
    payload = request.get_json(silent=True) or {}
    subject = str(payload.get("subject", "")).strip()
    category = str(payload.get("category", "")).strip()
    priority = str(payload.get("priority", "medium")).strip().lower()
    description = str(payload.get("description", "")).strip()
    allowed_categories = {"Payment", "Delivery", "Account", "Refund", "Product", "Other"}
    allowed_priorities = {"low", "medium", "high", "critical"}
    if not subject or not category or not description:
        return error_response("validation_error", "subject, category and description are required.")
    if len(subject) > 200 or len(description) > 5000:
        return error_response("validation_error", "Subject or description is too long.")
    if category not in allowed_categories or priority not in allowed_priorities:
        return error_response("validation_error", "Invalid category or priority.")
    ticket = Ticket(
        subject=subject, category=category, priority=priority, description=description,
        customer_id=g.api_user.id, sla_due_at=calculate_sla_due_at(priority),
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify({"data": ticket_payload(ticket)}), 201


@api_v1_bp.get("/tickets/<int:ticket_id>")
@api_token_required
def get_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if not ticket_access_allowed(g.api_user, ticket):
        return error_response("forbidden", "You do not have access to this ticket.", 403)
    return jsonify({"data": ticket_payload(ticket)})


@api_v1_bp.patch("/tickets/<int:ticket_id>")
@api_token_required
def update_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if g.api_user.role != "agent" or ticket.assigned_agent_id != g.api_user.id:
        return error_response("forbidden", "Only the assigned agent can update this ticket.", 403)
    payload = request.get_json(silent=True) or {}
    status = str(payload.get("status", "")).strip()
    success, message = transition_ticket(ticket, status)
    if not success:
        return error_response("invalid_transition", message, 409)
    db.session.commit()
    return jsonify({"data": ticket_payload(ticket), "message": message})


@api_v1_bp.post("/tickets/<int:ticket_id>/comments")
@api_token_required
def add_comment(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if not ticket_access_allowed(g.api_user, ticket):
        return error_response("forbidden", "You do not have access to this ticket.", 403)
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    is_internal = bool(payload.get("is_internal", False))
    if not message or len(message) > 5000:
        return error_response("validation_error", "message is required and must be 5,000 characters or fewer.")
    if is_internal and g.api_user.role not in {"agent", "admin"}:
        return error_response("forbidden", "Only agents and admins can add internal notes.", 403)
    comment = TicketComment(message=message, is_internal=is_internal, ticket_id=ticket.id, author_id=g.api_user.id)
    if not is_internal and g.api_user.role in {"agent", "admin"} and not ticket.first_responded_at:
        ticket.first_responded_at = datetime.utcnow()
    db.session.add(comment)
    db.session.commit()
    return jsonify({"data": {"id": comment.id, "message": comment.message, "is_internal": comment.is_internal}}), 201


@api_v1_bp.post("/tickets/<int:ticket_id>/assign")
@api_token_required
def assign_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if g.api_user.role != "admin":
        return error_response("forbidden", "Only admins can assign tickets.", 403)
    payload = request.get_json(silent=True) or {}
    agent_id = payload.get("agent_id")
    from app.models.user import User
    agent = db.session.get(User, agent_id)
    if not agent or agent.role != "agent" or not agent.is_active_account:
        return error_response("validation_error", "agent_id must reference an active agent.")
    ticket.assigned_agent_id = agent.id
    if ticket.status in {"open", "reopened"}:
        ticket.status = "assigned"
    db.session.commit()
    return jsonify({"data": ticket_payload(ticket)})


@api_v1_bp.post("/tickets/<int:ticket_id>/resolve")
@api_token_required
def resolve_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    if g.api_user.role != "agent" or ticket.assigned_agent_id != g.api_user.id:
        return error_response("forbidden", "Only the assigned agent can resolve this ticket.", 403)
    success, message = transition_ticket(ticket, "resolved")
    if not success:
        return error_response("invalid_transition", message, 409)
    db.session.commit()
    return jsonify({"data": ticket_payload(ticket), "message": message})
