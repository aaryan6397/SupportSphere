from datetime import datetime, timedelta

from app.models.ticket import Ticket
from app.models.user import User
from app.services.sla_service import ticket_sla_status
from app.services.workload_service import build_agent_workload


def build_ticket(priority="high", status="assigned", created_at=None):
    created_at = created_at or datetime.utcnow()
    return Ticket(
        subject="Support issue", category="Account", priority=priority,
        description="Details", customer_id=1, assigned_agent_id=2,
        status=status, created_at=created_at,
        sla_due_at=created_at + timedelta(hours=8),
    )


def test_sla_marks_unanswered_overdue_first_response_as_breached():
    ticket = build_ticket(created_at=datetime.utcnow() - timedelta(hours=2))
    assert ticket_sla_status(ticket) == "BREACHED"


def test_sla_marks_resolved_ticket_as_completed():
    ticket = build_ticket(status="resolved")
    assert ticket_sla_status(ticket) == "COMPLETED"


def test_workload_recommends_lowest_weighted_agent():
    first = User(id=1, name="Busy Agent", email="busy@example.com", role="agent")
    second = User(id=2, name="Available Agent", email="available@example.com", role="agent")
    critical_ticket = build_ticket(priority="critical")
    critical_ticket.assigned_agent_id = first.id

    workloads, recommendation = build_agent_workload([first, second], [critical_ticket])
    assert recommendation["id"] == second.id
    assert workloads[0]["name"] == "Available Agent"
