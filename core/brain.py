from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import BaseModel, Field

from config import get_settings
from core.tools import (
    check_google_calendar,
    fetch_recent_notes,
    send_sms_summary_to_me,
)


class ChatMessage(BaseModel):
    role: str
    content: str


class LLMRequest(BaseModel):
    system_instructions: str
    user_context: str = ""
    chat_history: list[ChatMessage] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


TOOLS_REGISTRY = {
    "check_google_calendar": check_google_calendar,
    "send_sms_summary_to_me": send_sms_summary_to_me,
    "fetch_recent_notes": fetch_recent_notes,
}


class Brain:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self.client.aclose()

    async def reason(
        self,
        system_instructions: str,
        user_context: str = "",
        chat_history: list[ChatMessage] | None = None,
        use_tools: list[str] | None = None,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": system_instructions},
        ]
        if user_context:
            messages.append({"role": "system", "content": f"Context: {user_context}"})
        if chat_history:
            messages.extend([{"role": m.role, "content": m.content} for m in chat_history])

        tools_schema = []
        if use_tools:
            for name in use_tools:
                # Minimal schema generation placeholder; extend as needed
                tools_schema.append({"type": "function", "function": {"name": name}})

        # Prefer OpenAI, fallback to OpenRouter
        if self.settings.has_openai:
            response = await self._call_openai(messages, tools_schema)
        elif self.settings.has_openrouter:
            response = await self._call_openrouter(messages, tools_schema)
        else:
            raise RuntimeError("No LLM provider configured")

        # Simple tool calling loop (one round)
        tool_calls = response.get("tool_calls", [])
        tool_results = []
        for call in tool_calls:
            name = call.get("name")
            args = call.get("arguments", {})
            if name in TOOLS_REGISTRY:
                try:
                    result = await TOOLS_REGISTRY[name](**args)
                    tool_results.append({"name": name, "result": result})
                except Exception as e:
                    tool_results.append({"name": name, "error": str(e)})

        return {
            "llm_output": response.get("content"),
            "tool_calls": tool_calls,
            "tool_results": tool_results,
            "model": response.get("model"),
        }

    async def _call_openai(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.openai_model,
            "messages": messages,
            "tools": tools or None,
            "tool_choice": "auto" if tools else None,
        }
        resp = await self.client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]["message"]
        return {
            "content": choice.get("content"),
            "tool_calls": self._parse_openai_tool_calls(choice.get("tool_calls")),
            "model": data.get("model"),
        }

    async def _call_openrouter(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key.get_secret_value()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
        }
        payload = {
            "model": self.settings.openrouter_model,
            "messages": messages,
            "tools": tools or None,
        }
        resp = await self.client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]["message"]
        return {
            "content": choice.get("content"),
            "tool_calls": self._parse_openrouter_tool_calls(choice.get("tool_calls")),
            "model": data.get("model"),
        }

    @staticmethod
    def _parse_openai_tool_calls(tool_calls: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        out = []
        if not tool_calls:
            return out
        for tc in tool_calls:
            try:
                args = json.loads(tc["function"]["arguments"])
            except Exception:
                args = {}
            out.append({"name": tc["function"]["name"], "arguments": args})
        return out

    @staticmethod
    def _parse_openrouter_tool_calls(tool_calls: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        return Brain._parse_openai_tool_calls(tool_calls)
