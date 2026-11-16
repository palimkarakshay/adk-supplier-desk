"""MCP server (stdio) that exposes the order system to the agent.

Every tool takes supplier_id. The agent-side guardrail overwrites that argument from session
state, so the model never chooses whose data it reads.
"""
from mcp.server.mcpserver import MCPServer

from supplier_desk.data import ASNS, ORDERS

mcp = MCPServer("order-system")


@mcp.tool()
def get_order_status(order_id: str, supplier_id: str) -> dict:
    """Return part, open quantity, next delivery date and firm/forecast status for one scheduling agreement."""
    order = ORDERS.get(order_id.strip().upper())
    if not order or order["supplier_id"] != supplier_id:
        return {"found": False, "order_id": order_id}
    return {"found": True, "order_id": order_id.strip().upper(), **{k: v for k, v in order.items() if k != "supplier_id"}}


@mcp.tool()
def list_asns(supplier_id: str, order_id: str = "") -> dict:
    """List advance ship notices for the supplier, optionally for one scheduling agreement."""
    rows = [a for a in ASNS if a["supplier_id"] == supplier_id and (not order_id or a["order_id"] == order_id.strip().upper())]
    return {"asns": [{k: v for k, v in a.items() if k != "supplier_id"} for a in rows]}


if __name__ == "__main__":
    mcp.run()
