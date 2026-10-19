"""Thin Gemini wrapper: prompt templates, structured output, on-disk cache."""

from __future__ import annotations

import hashlib
import json
import time
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from . import config

T = TypeVar("T", bound=BaseModel)


timings: list[tuple[str, float]] = []  # (prompt, seconds) of uncached calls in this process


class LLMError(RuntimeError):
    pass


def render(template: str, **values: str) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def generate(prompt_name: str, schema: type[T], use_cache: bool = True, **values: str) -> T:
    prompt = render(config.prompt(prompt_name), **values)
    model = config.gemini_model()
    key = hashlib.sha256(
        json.dumps([model, prompt, schema.__name__, schema.model_json_schema()], sort_keys=True).encode()
    ).hexdigest()[:24]
    cache_file = config.ROOT / config.settings()["llm"]["cache_dir"] / f"{prompt_name}_{key}.json"

    if use_cache and cache_file.exists():
        return schema.model_validate_json(cache_file.read_text())

    started = time.perf_counter()
    text = _call(model, prompt, schema, prompt_name)
    timings.append((prompt_name, round(time.perf_counter() - started, 1)))
    try:
        result = schema.model_validate_json(text)
    except ValidationError as e:
        raise LLMError(f"{prompt_name}: response did not match schema: {e}") from e

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(result.model_dump_json(indent=2))
    return result


def _call(model: str, prompt: str, schema: type[BaseModel], prompt_name: str = "default") -> str:
    key = config.gemini_key()
    if not key:
        raise LLMError("GEMINI_API_KEY is not set (put it in .env)")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    llm = config.settings()["llm"]
    cfg = types.GenerateContentConfig(
        temperature=llm["temperature"],
        max_output_tokens=llm["max_output_tokens"],
        response_mime_type="application/json",
        response_json_schema=schema.model_json_schema(),
        thinking_config=types.ThinkingConfig(thinking_budget=_budget(llm["thinking_budget"], prompt_name, model)),
    )
    last: Exception | None = None
    for attempt in range(3):
        try:
            resp = client.models.generate_content(model=model, contents=prompt, config=cfg)
            finish = _finish(resp)
            if not resp.text or "MAX_TOKENS" in finish:
                raise LLMError(f"incomplete response (finish reason: {finish})")
            return resp.text
        except Exception as e:  # network / quota / empty
            last = e
            time.sleep(2 * (attempt + 1))
    raise LLMError(f"Gemini call failed after 3 attempts: {last}")


def _budget(cfg, prompt_name: str, model: str) -> int:
    n = cfg if isinstance(cfg, int) else int(cfg.get(prompt_name, cfg.get("default", 2048)))
    return max(n, 128) if "pro" in model else n  # Pro models can't turn thinking off


def _finish(resp) -> str:
    try:
        return str(resp.candidates[0].finish_reason)
    except Exception:
        return "unknown"
