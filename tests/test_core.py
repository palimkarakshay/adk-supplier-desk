"""Offline tests. No model calls."""
from types import SimpleNamespace

from supplier_desk.guardrails import MAX_TICKETS_PER_SESSION, scope_to_supplier
from supplier_desk.order_mcp_server import get_order_status, list_asns
from supplier_desk.retrieval import POLICY_INDEX


def ctx(**state):
    return SimpleNamespace(state=dict(state))


def tool(name):
    return SimpleNamespace(name=name)


def test_retrieval_ranks_chargeback_passage_first():
    assert POLICY_INDEX.search("charge for a late ASN")[0]["id"] == "P2"


def test_retrieval_ranks_firm_window_first():
    assert POLICY_INDEX.search("can I change a firm schedule line")[0]["id"] == "P3"


def test_retrieval_returns_nothing_for_unrelated_query():
    assert POLICY_INDEX.search("zebra umbrella") == []


def test_guardrail_overwrites_model_supplied_supplier():
    c, args = ctx(supplier_id="S-1042"), {"order_id": "SA-61010", "supplier_id": "S-2077"}
    assert scope_to_supplier(tool("get_order_status"), args, c) is None
    assert args["supplier_id"] == "S-1042"
    assert c.state["scope_overrides"] == 1


def test_guardrail_blocks_without_authenticated_supplier():
    assert scope_to_supplier(tool("list_asns"), {}, ctx())["blocked"] is True


def test_guardrail_caps_tickets():
    c = ctx(supplier_id="S-1042", tickets=[{}] * MAX_TICKETS_PER_SESSION)
    assert scope_to_supplier(tool("open_ticket"), {"summary": "x"}, c)["blocked"] is True


def test_order_system_hides_other_suppliers_orders():
    assert get_order_status("SA-61010", "S-1042") == {"found": False, "order_id": "SA-61010"}
    assert get_order_status("SA-55001", "S-1042")["next_delivery"] == "2026-11-19"


def test_asn_list_is_scoped():
    assert {a["asn"] for a in list_asns("S-1042")["asns"]} == {"ASN-90311", "ASN-90340"}
