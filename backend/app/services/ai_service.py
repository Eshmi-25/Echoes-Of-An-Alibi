import json
import time

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.core.config import Settings


class AIInternalFlags(BaseModel):
    evasive: bool = False
    possible_contradiction: bool = False


class AIResponse(BaseModel):
    dialogue: str
    emotion: str = "calm"
    revealed_fact_ids: list[str] = Field(default_factory=list)
    referenced_clue_ids: list[str] = Field(default_factory=list)
    suggested_topic_ids: list[str] = Field(default_factory=list)
    internal_flags: AIInternalFlags = Field(default_factory=AIInternalFlags)


class AIService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(self, prompt: str, fallback_payload: dict) -> tuple[AIResponse, dict]:
        started = time.perf_counter()
        if self.settings.ollama_enabled:
            try:
                async with httpx.AsyncClient(timeout=self.settings.ollama_timeout_seconds) as client:
                    res = await client.post(
                        f"{self.settings.ollama_base_url}/api/generate",
                        json={
                            "model": self.settings.ollama_model,
                            "prompt": prompt,
                            "stream": False,
                            "format": "json",
                        },
                    )
                    res.raise_for_status()
                    text = res.json().get("response", "{}")
                    parsed = AIResponse.model_validate(json.loads(text))
                    return parsed, {
                        "provider": "ollama",
                        "model": self.settings.ollama_model,
                        "latency_ms": int((time.perf_counter() - started) * 1000),
                        "prompt_version": self.settings.ai_prompt_version,
                    }
            except (httpx.HTTPError, ValidationError, json.JSONDecodeError):
                pass

        reply = AIResponse.model_validate(
            {
                "dialogue": fallback_payload["dialogue"],
                "emotion": fallback_payload.get("emotion", "calm"),
                "revealed_fact_ids": fallback_payload.get("revealed_fact_ids", []),
                "referenced_clue_ids": fallback_payload.get("referenced_clue_ids", []),
                "suggested_topic_ids": fallback_payload.get("suggested_topic_ids", []),
                "internal_flags": fallback_payload.get("internal_flags", {}),
            }
        )
        return reply, {
            "provider": "fallback",
            "model": "deterministic-template",
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "prompt_version": self.settings.ai_prompt_version,
        }
