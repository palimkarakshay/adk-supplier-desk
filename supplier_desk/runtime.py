"""Runs one conversation and writes a JSONL trace: who spoke, which tool, what came back, tokens and latency."""
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

APP = "supplier_desk"


class Desk:
    def __init__(self, supplier_id: str, supplier_name: str, trace_path: Path | None = None):
        from .agent import root_agent

        self.sessions = InMemorySessionService()
        self.runner = Runner(app_name=APP, agent=root_agent, session_service=self.sessions)
        self.user, self.session_id = supplier_id, f"s-{int(time.time() * 1000)}"
        self.state0 = {"supplier_id": supplier_id, "supplier_name": supplier_name}
        self.trace_path = trace_path
        self.started = False

    def _log(self, row: dict):
        if self.trace_path:
            with self.trace_path.open("a") as f:
                f.write(json.dumps(row, default=str) + "\n")

    async def ask(self, text: str) -> dict:
        if not self.started:
            await self.sessions.create_session(app_name=APP, user_id=self.user, session_id=self.session_id, state=self.state0)
            self.started = True
        self._log({"type": "user", "text": text})
        t0, last = time.time(), time.time()
        answer, tools, agents, tokens = "", [], [], 0
        msg = types.Content(role="user", parts=[types.Part(text=text)])
        async for ev in self.runner.run_async(user_id=self.user, session_id=self.session_id, new_message=msg):
            now = time.time()
            usage = getattr(ev, "usage_metadata", None)
            tok = (usage.total_token_count or 0) if usage else 0
            tokens += tok
            base = {"agent": ev.author, "ms": int((now - last) * 1000), "tokens": tok}
            last = now
            if ev.author not in agents:
                agents.append(ev.author)
            if ev.actions and ev.actions.transfer_to_agent:
                self._log({**base, "type": "transfer", "to": ev.actions.transfer_to_agent})
            for part in (ev.content.parts if ev.content and ev.content.parts else []):
                if part.function_call and part.function_call.name != "transfer_to_agent":
                    tools.append(part.function_call.name)
                    self._log({**base, "type": "tool_call", "tool": part.function_call.name, "args": dict(part.function_call.args or {})})
                elif part.function_response and part.function_response.name != "transfer_to_agent":
                    self._log({**base, "type": "tool_result", "tool": part.function_response.name, "result": part.function_response.response})
                elif part.text and part.text.strip() and not getattr(part, "thought", False):
                    self._log({**base, "type": "text", "text": part.text.strip()})
                    if ev.author != "policy_critic":
                        answer = part.text.strip()
        session = await self.sessions.get_session(app_name=APP, user_id=self.user, session_id=self.session_id)
        result = {"answer": answer, "tools": tools, "agents": agents, "tokens": tokens,
                  "ms": int((time.time() - t0) * 1000), "state": dict(session.state)}
        self._log({"type": "turn_end", "tokens": tokens, "ms": result["ms"]})
        return result

    async def close(self):
        await self.runner.close()
