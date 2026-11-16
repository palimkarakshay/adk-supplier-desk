# adk-supplier-desk

A supplier service desk for a fictional assembly plant, built on Google ADK 2.14 and Gemini. All data is fixture data.

```
desk_router              routes each turn
  order_agent            reads the order system through an MCP server, can open a ticket
  policy_agent (loop)    policy_writer drafts from retrieved passages, policy_critic checks grounding
```

- `supplier_desk/agent.py` - the agents
- `supplier_desk/order_mcp_server.py` - MCP server (stdio) for orders and ASNs
- `supplier_desk/guardrails.py` - before-tool guardrail: supplier_id always comes from session state, tickets are capped
- `supplier_desk/retrieval.py` - BM25 over the policy manual, passage ids for citations
- `supplier_desk/runtime.py` - runs a conversation and writes a JSONL trace (agent, tool, tokens, timing)
- `supplier_desk/limits.py` - pacing for the Gemini free tier
- `evals/` - 8 golden cases, 2 of them data-leak cases. `tests/` - 8 offline tests

## Run

```
uv venv .venv && uv pip install --python .venv/bin/python google-adk mcp python-dotenv pytest
echo "GOOGLE_API_KEY=<free-tier AI Studio key>" > .env      # never a Vertex or billed project
.venv/bin/python -m pytest -q tests        # offline
.venv/bin/python run_demo.py               # 4-turn conversation, writes traces/demo.jsonl
.venv/bin/python evals/run_evals.py        # golden set, exit 1 on any failure
```

Model: `SUPPLIER_DESK_MODEL` (default `gemini-3.5-flash-lite`). Free-tier daily request caps are small, so one demo plus one eval run is about a day's quota on one model.

## Results (2026-11-16)

Offline tests 8/8. Golden set 7/8 on the first run: the router sent a charge dispute to the policy agent and no ticket was opened. After the routing rule fix, 8/8.

## Notes

- mcp 2.x renamed FastMCP to MCPServer.
- Not built: CX Agent Studio / Dialogflow. Those need a Google Cloud project with billing.
