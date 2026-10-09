from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.audit_log import AuditLog


def record_audit_event(response):
    if request.method != "POST":
        return response

    if response.status_code >= 400:
        return response

    if not current_user.is_authenticated:
        return response

    event_map = {
        "tickets.create_ticket": {
            "action": "ticket_created",
            "description": "Created a new support ticket.",
            "entity_type": "ticket"
        },

        "tickets.add_comment": {
            "action": "ticket_reply_added",
            "description": "Added a reply to a support ticket.",
            "entity_type": "ticket"
        },

        "tickets.submit_feedback": {
            "action": "feedback_submitted",
            "description": "Submitted customer feedback for a resolved ticket.",
            "entity_type": "ticket"
        },

        "agent.update_ticket_status": {
            "action": "ticket_status_updated",
            "description": "Updated a ticket status.",
            "entity_type": "ticket"
        },

        "admin.assign_ticket": {
            "action": "ticket_assigned",
            "description": "Assigned a ticket to a support agent.",
            "entity_type": "ticket"
        },

        "admin.create_agent": {
            "action": "agent_created",
            "description": "Created a new support agent account.",
            "entity_type": "user"
        }
    }

    event = event_map.get(request.endpoint)

    if not event:
        return response

    ticket_id = None

    if request.view_args:
        ticket_id = request.view_args.get("ticket_id")

    try:
        audit_log = AuditLog(
            action=event["action"],
            description=event["description"],
            entity_type=event["entity_type"],
            entity_id=ticket_id,
            actor_id=current_user.id
        )

        db.session.add(audit_log)
        db.session.commit()

    except Exception:
        db.session.rollback()

    return response