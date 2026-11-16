"""Supplier service desk on Google ADK.

desk_router            routes each turn
  order_agent          reads the order system through MCP tools, can open a ticket
  policy_agent (loop)  policy_writer drafts from retrieved passages, policy_critic checks grounding
"""
import os
import sys
from pathlib import Path

from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import McpToolset, exit_loop
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

from .guardrails import scope_to_supplier
from .limits import pace
from .tools import open_ticket, search_policy

MODEL = os.environ.get("SUPPLIER_DESK_MODEL", "gemini-3.5-flash-lite")
ROOT = Path(__file__).resolve().parent.parent

order_system = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["-m", "supplier_desk.order_mcp_server"],
            cwd=str(ROOT),
        ),
        timeout=20,
    ),
    tool_filter=["get_order_status", "list_asns"],
)

order_agent = LlmAgent(
    name="order_agent",
    model=MODEL,
    before_model_callback=pace,
    description="Answers questions about scheduling agreements, delivery dates and ASNs. Opens tickets for a human buyer.",
    instruction=(
        "You work the supplier service desk for an assembly plant. The signed-in supplier is "
        "{supplier_name} ({supplier_id}).\n"
        "Use get_order_status and list_asns for any question about an order or shipment. Never guess a date or quantity.\n"
        "If a tool says found is false, say you cannot find that order for this supplier. Do not speculate about other suppliers.\n"
        "If the supplier asks for a person or disputes a charge, call open_ticket and give the ticket id.\n"
        "Answer in two or three short sentences."
    ),
    tools=[order_system, open_ticket],
    before_tool_callback=scope_to_supplier,
)

policy_writer = LlmAgent(
    name="policy_writer",
    model=MODEL,
    before_model_callback=pace,
    instruction=(
        "Answer the supplier's policy question. First call search_policy. Use only the returned passages.\n"
        "Cite the passage id after each fact, like [P2]. If the passages do not cover the question, say so.\n"
        "Reviewer feedback on your last draft, if any: {feedback?}\n"
        "Answer in two or three short sentences."
    ),
    tools=[search_policy],
    output_key="draft",
    before_tool_callback=scope_to_supplier,
)

policy_critic = LlmAgent(
    name="policy_critic",
    model=MODEL,
    before_model_callback=pace,
    instruction=(
        "You review a draft answer against policy passages.\n"
        "Passages:\n{passages?}\n\nDraft:\n{draft?}\n\n"
        "If every fact in the draft is supported by the passages and carries a passage id, call exit_loop and say nothing else.\n"
        "Otherwise reply with one sentence that names the unsupported fact."
    ),
    tools=[exit_loop],
    output_key="feedback",
    include_contents="none",
)

policy_agent = LoopAgent(
    name="policy_agent",
    description="Answers supplier policy questions (ASN rules, chargebacks, firm windows, labels, invoices) with cited passages.",
    sub_agents=[policy_writer, policy_critic],
    max_iterations=2,
)

root_agent = LlmAgent(
    name="desk_router",
    model=MODEL,
    before_model_callback=pace,
    description="Front door of the supplier service desk.",
    instruction=(
        "You are the front door of a supplier service desk. Do not answer questions yourself.\n"
        "Transfer order, delivery, shipment, ASN status and ticket requests to order_agent.\n"
        "A dispute, a complaint or a request for a person or a call back always goes to order_agent, even when it mentions a charge or a rule.\n"
        "Transfer questions about rules, charges, windows, labels and invoices to policy_agent.\n"
        "For a greeting or anything off topic, reply in one sentence and say what the desk can help with."
    ),
    sub_agents=[order_agent, policy_agent],
)
