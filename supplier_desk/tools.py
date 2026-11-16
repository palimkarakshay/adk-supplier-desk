"""Local tools: policy retrieval and the one write action (opening a ticket)."""
from google.adk.tools import ToolContext

from .retrieval import POLICY_INDEX


def search_policy(query: str, tool_context: ToolContext) -> dict:
    """Search the supplier policy manual. Returns the best passages with their ids, for example P2."""
    hits = POLICY_INDEX.search(query, k=2)
    tool_context.state["passages"] = "\n".join(f"[{h['id']}] {h['title']}: {h['text']}" for h in hits) or "none"
    return {"passages": [{"id": h["id"], "title": h["title"], "text": h["text"]} for h in hits]}


def open_ticket(summary: str, supplier_id: str, tool_context: ToolContext) -> dict:
    """Open a ticket for a human buyer. Use when the supplier asks for a person or disputes a charge."""
    tickets = tool_context.state.get("tickets", [])
    ticket = {"id": f"T-{7001 + len(tickets)}", "supplier_id": supplier_id, "summary": summary[:200]}
    tool_context.state["tickets"] = tickets + [ticket]
    return {"opened": True, "ticket_id": ticket["id"], "queue": "buyer desk", "sla_hours": 8}
