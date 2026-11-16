"""Tool guardrail. Runs before every tool call."""
import logging

log = logging.getLogger("supplier_desk.guardrail")

MAX_TICKETS_PER_SESSION = 2


def scope_to_supplier(tool, args, context):
    """Force supplier_id from session state and cap write actions.

    Returning a dict skips the tool and hands that dict to the model as the tool result.
    """
    supplier = context.state.get("supplier_id")
    if "supplier_id" in args or tool.name in ("get_order_status", "list_asns", "open_ticket"):
        if not supplier:
            return {"blocked": True, "reason": "no authenticated supplier in session"}
        asked = args.get("supplier_id")
        if asked and asked != supplier:
            log.warning("model asked for supplier %s, session is %s, overwritten", asked, supplier)
            overrides = context.state.get("scope_overrides", 0)
            context.state["scope_overrides"] = overrides + 1
        args["supplier_id"] = supplier
    if tool.name == "open_ticket" and len(context.state.get("tickets", [])) >= MAX_TICKETS_PER_SESSION:
        return {"blocked": True, "reason": "ticket limit reached for this session"}
    return None
