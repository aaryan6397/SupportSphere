from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models.ticket import Ticket
from app.models.user import User


TICKET_STATUSES = {"open", "assigned", "in_progress", "waiting_customer", "resolved", "closed", "reopened", "escalated"}
TICKET_PRIORITIES = {"low", "medium", "high", "critical"}
TICKET_CATEGORIES = {"Payment", "Delivery", "Account", "Refund", "Product", "Other"}
PAGE_SIZES = {10, 25, 50, 100}


def normalize_filters(values):
    """Return validated filters safe to use in ticket listing queries."""
    status = values.get("status", "")
    priority = values.get("priority", "")
    category = values.get("category", "")
    per_page = values.get("per_page", 10, type=int)
    return {
        "q": values.get("q", "").strip()[:120],
        "status": status if status in TICKET_STATUSES else "",
        "priority": priority if priority in TICKET_PRIORITIES else "",
        "category": category if category in TICKET_CATEGORIES else "",
        "per_page": per_page if per_page in PAGE_SIZES else 10,
    }


def filtered_ticket_query(filters, customer_id=None, agent_id=None):
    """Build an efficient ticket query for a role-scoped dashboard."""
    query = Ticket.query.options(joinedload(Ticket.customer), joinedload(Ticket.assigned_agent))
    if customer_id is not None:
        query = query.filter(Ticket.customer_id == customer_id)
    if agent_id is not None:
        query = query.filter(Ticket.assigned_agent_id == agent_id)
    if filters["q"]:
        needle = f"%{filters['q']}%"
        query = query.join(Ticket.customer).filter(or_(
            Ticket.ticket_code.ilike(needle), Ticket.subject.ilike(needle), User.name.ilike(needle)
        ))
    if filters["status"]:
        query = query.filter(Ticket.status == filters["status"])
    if filters["priority"]:
        query = query.filter(Ticket.priority == filters["priority"])
    if filters["category"]:
        query = query.filter(Ticket.category == filters["category"])
    return query.order_by(Ticket.updated_at.desc())


def paginate_tickets(query, page, per_page):
    return query.paginate(page=page, per_page=per_page, error_out=False)
