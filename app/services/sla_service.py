from datetime import datetime, timedelta


SLA_POLICIES = {
    "critical": {"first_response_minutes": 15, "resolution_minutes": 4 * 60},
    "high": {"first_response_minutes": 60, "resolution_minutes": 8 * 60},
    "medium": {"first_response_minutes": 4 * 60, "resolution_minutes": 24 * 60},
    "low": {"first_response_minutes": 8 * 60, "resolution_minutes": 48 * 60},
}


def calculate_sla_due_at(priority, created_at=None):
    created_at = created_at or datetime.utcnow()
    policy = SLA_POLICIES.get(priority, SLA_POLICIES["medium"])
    return created_at + timedelta(minutes=policy["resolution_minutes"])


def ticket_sla_status(ticket, now=None):
    """Return WITHIN_SLA, AT_RISK, BREACHED or COMPLETED for a ticket."""
    if ticket.status in {"resolved", "closed"}:
        return "COMPLETED"
    now = now or datetime.utcnow()
    policy = SLA_POLICIES.get(ticket.priority, SLA_POLICIES["medium"])
    first_response_deadline = ticket.created_at + timedelta(
        minutes=policy["first_response_minutes"]
    )
    resolution_deadline = ticket.sla_due_at or calculate_sla_due_at(ticket.priority, ticket.created_at)
    if (not ticket.first_responded_at and now > first_response_deadline) or now > resolution_deadline:
        return "BREACHED"
    response_remaining = (first_response_deadline - now).total_seconds() / 60
    resolution_remaining = (resolution_deadline - now).total_seconds() / 60
    warning_window = max(15, policy["resolution_minutes"] * 0.25)
    if not ticket.first_responded_at and response_remaining <= max(5, policy["first_response_minutes"] * 0.25):
        return "AT_RISK"
    if resolution_remaining <= warning_window:
        return "AT_RISK"
    return "WITHIN_SLA"
