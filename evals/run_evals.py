"""Golden-set eval. Each case runs in a fresh session as supplier S-1042 and is scored on
tool trajectory, required facts and citations, and data-leak checks. Exit code 1 on any failure."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from supplier_desk.runtime import Desk  # noqa: E402

HERE = Path(__file__).resolve().parent


def score(case: dict, out: dict) -> list[str]:
    fails, answer = [], out["answer"]
    for t in case.get("tools", []):
        if t not in out["tools"]:
            fails.append(f"missing tool {t}")
    if case.get("no_tools") and out["tools"]:
        fails.append(f"unexpected tools {out['tools']}")
    for s in case.get("must", []):
        if s not in answer:
            fails.append(f"answer lacks {s}")
    for s in case.get("must_not", []):
        if s in answer:
            fails.append(f"LEAK {s}")
    if "ticket_supplier" in case:
        tickets = out["state"].get("tickets", [])
        if len(tickets) != 1 or tickets[0]["supplier_id"] != case["ticket_supplier"]:
            fails.append("ticket missing or wrong supplier")
    return fails


async def main():
    cases = json.loads((HERE / "cases.json").read_text())
    only = set(sys.argv[1:])
    rows = []
    for case in cases:
        if only and case["id"] not in only:
            continue
        desk = Desk("S-1042", "Kestrel Stamping", HERE.parent / "traces" / f"eval-{case['id']}.jsonl")
        desk.trace_path.unlink(missing_ok=True)
        try:
            out = await desk.ask(case["ask"])
            fails = score(case, out)
        except Exception as e:  # quota or transport error is reported, not hidden
            out, fails = {"answer": "", "tools": [], "tokens": 0, "ms": 0}, [f"ERROR {type(e).__name__}"]
        rows.append({"id": case["id"], "pass": not fails, "fails": fails, "tools": out["tools"],
                     "tokens": out["tokens"], "ms": out["ms"], "answer": out["answer"][:300]})
        print(("PASS " if not fails else "FAIL ") + case["id"], fails or "", flush=True)
    passed = sum(r["pass"] for r in rows)
    (HERE / "report.json").write_text(json.dumps({"passed": passed, "total": len(rows), "rows": rows}, indent=2))
    print(f"\n{passed}/{len(rows)} passed")
    sys.exit(0 if passed == len(rows) else 1)


asyncio.run(main())
