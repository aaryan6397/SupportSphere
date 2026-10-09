from datetime import datetime

from app.models.ticket import calculate_sla_due_at


VALID_TRANSITIONS = {
    "open": {"assigned"},
    "assigned": {"in_progress", "waiting_customer", "resolved", "escalated"},
    "in_progress": {"waiting_customer", "resolved", "escalated"},
    "waiting_customer": {"in_progress", "resolved", "escalated"},
    "escalated": {"assigned", "in_progress", "resolved"},
    "resolved": {"closed", "reopened"},
    "closed": {"reopened"},
    "reopened": {"assigned", "in_progress", "escalated"},
}


def transition_ticket(ticket, next_status):
    """Apply a valid lifecycle transition and return a (success, message) tuple."""
    if next_status == ticket.status:
        return True, "Ticket status is already up to date."

    allowed_next_statuses = VALID_TRANSITIONS.get(ticket.status, set())
    if next_status not in allowed_next_statuses:
        return False, (
            f"Cannot move a {ticket.status.replace('_', ' ')} ticket "
            f"directly to {next_status.replace('_', ' ')}."
        )

    ticket.status = next_status

    if next_status == "resolved":
        ticket.resolved_at = datetime.utcnow()
    elif next_status == "reopened":
        ticket.resolved_at = None
        ticket.sla_due_at = calculate_sla_due_at(ticket.priority)

    return True, "Ticket status updated successfully."
