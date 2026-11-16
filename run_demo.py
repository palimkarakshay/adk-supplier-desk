"""Scripted demo conversation. Writes traces/demo.jsonl."""
import asyncio
from pathlib import Path

from supplier_desk.runtime import Desk

TURNS = [
    "Hi, when is the next delivery due on SA-55001 and has the ASN gone out?",
    "What happens if that ASN goes out late?",
    "Can you also check SA-61010 for me?",
    "I want to dispute a late ASN charge from last week. Can someone call me?",
]


async def main():
    trace = Path("traces/demo.jsonl")
    trace.unlink(missing_ok=True)
    desk = Desk("S-1042", "Kestrel Stamping", trace)
    for turn in TURNS:
        out = await desk.ask(turn)
        print(f"\nSUPPLIER: {turn}\nDESK [{' > '.join(out['agents'])}] tools={out['tools']} {out['tokens']} tok {out['ms']} ms\n{out['answer']}")
    await desk.close()


asyncio.run(main())
