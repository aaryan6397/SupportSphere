from app.services.sla_service import ticket_sla_status


def build_agent_workload(agents, tickets):
    """Build workload metrics and a transparent recommendation for admins."""
    by_agent = {agent.id: {"id": agent.id, "name": agent.name, "active": 0, "high": 0, "critical": 0, "resolved": 0, "at_risk": 0, "breached": 0} for agent in agents}
    for ticket in tickets:
        if ticket.assigned_agent_id not in by_agent:
            continue
        metrics = by_agent[ticket.assigned_agent_id]
        if ticket.status == "resolved":
            metrics["resolved"] += 1
        if ticket.status not in {"resolved", "closed"}:
            metrics["active"] += 1
            if ticket.priority == "high":
                metrics["high"] += 1
            if ticket.priority == "critical":
                metrics["critical"] += 1
            status = ticket_sla_status(ticket)
            if status == "AT_RISK":
                metrics["at_risk"] += 1
            elif status == "BREACHED":
                metrics["breached"] += 1
    workloads = list(by_agent.values())
    for workload in workloads:
        workload["score"] = workload["active"] + workload["high"] * 2 + workload["critical"] * 3 + workload["breached"] * 2
    workloads.sort(key=lambda item: (item["score"], item["active"], item["name"].lower()))
    recommendation = workloads[0] if workloads else None
    return workloads, recommendation
