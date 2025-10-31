import os, json
from typing import Dict, Any
import requests


def _safe_text(value: Any) -> str:

    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return ""
    return str(value)


def _use_llm() -> bool:
    return os.environ.get("USE_LLM", "false").lower() in {"1", "true", "yes"}


def _llm_chat(prompt: str, diffs: str, ast_summary: Dict) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not (api_key and _use_llm()):
        return ""
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    # Compact AST summary to avoid sending large payloads
    file_list = list((ast_summary or {}).keys())[:50]
    ast_hint = f"Files analyzed: {len(file_list)} (e.g., {', '.join(file_list[:5])})"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Diff length: {len(diffs or '')} characters. {ast_hint}. Provide concise, actionable output."},
    ]
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.2,
            },
            timeout=3,
        )
        resp.raise_for_status()
        data = resp.json()
        return _safe_text(((data.get("choices") or [{}])[0].get("message") or {}).get("content"))
    except Exception:
        return ""


def call_dev_agent(prompt: str, diffs: str, ast_summary: Dict) -> Dict[str, str]:
    text = _llm_chat(prompt, diffs, ast_summary) or (
        f"Developer summary based on diffs ({len(diffs or '')} chars) and {len(ast_summary or {})} files analyzed."
    )
    return {"text": _safe_text(text)}


def call_arch_agent(prompt: str, diffs: str, ast_summary: Dict) -> Dict[str, str]:
    text = _llm_chat(prompt, diffs, ast_summary) or (
        "Architecture taxonomy: potential areas touched include auth, validation, and configuration."
    )
    return {"text": _safe_text(text)}


def call_sec_agent(prompt: str, diffs: str, ast_summary: Dict) -> Dict[str, str]:
    text = _llm_chat(prompt, diffs, ast_summary) or (
        "Security posture: review input validation, secrets handling, and dependency versions."
    )
    return {"text": _safe_text(text)}


