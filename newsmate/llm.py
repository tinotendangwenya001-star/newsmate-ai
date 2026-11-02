"""Thin wrapper around the Claude API."""
import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("NEWSMATE_MODEL", "claude-sonnet-4-6")
_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    return _client


def ask(system: str, user: str, max_tokens: int = 2000) -> str:
    resp = _get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def ask_json(system: str, user: str, max_tokens: int = 3000) -> dict:
    raw = ask(system + "\nRespond with a single valid JSON object and nothing else.", user, max_tokens)
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model did not return JSON:\n" + raw[:300])
    return json.loads(raw[start : end + 1])
