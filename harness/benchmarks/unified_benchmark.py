#!/usr/bin/env python3
"""Unified Benchmark - loads from ~/.factory/config.json"""

import asyncio
import json
import time
import httpx
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path.home() / ".factory" / "config.json"
CLIPROXY_URL = "http://localhost:8317"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def find_model(models: list, suffix: str = None) -> dict:
    for m in models:
        name = m.get("model_display_name", m.get("model", ""))
        if suffix and suffix in name:
            return m
    return models[0] if models else {}


@dataclass
class Result:
    model: str
    latency_ms: float
    success: bool
    source: str
    error: str = ""


async def run_model(model_cfg: dict, prompt: str = "hi") -> Result:
    model = model_cfg.get("model_display_name", "unknown")
    base_url = model_cfg.get("base_url", "")
    api_key = model_cfg.get("api_key", "")
    
    # Try cliproxy
    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(f"{CLIPROXY_URL}/v1/chat/completions",
                json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 20})
            if r.status_code == 200:
                return Result(model, 100, True, "cliproxy")
    except Exception as e:
        pass
    
    # Direct
    if not api_key or "dummy" in api_key.lower():
        return Result(model, 0, False, "direct", "no key")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as c:
            start = time.perf_counter()
            r = await c.post(f"{base_url}/v1/messages",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 20})
            lat = (time.perf_counter() - start) * 1000
            return Result(model, lat, r.status_code == 200, "direct", str(r.status_code) if r.status_code != 200 else "")
    except Exception as e:
        return Result(model, 0, False, "direct", str(e)[:50])


async def main():
    cfg = load_config()
    models = cfg.get("custom_models", [])
    
    # Find minimax
    m = find_model(models, "minimax")
    if not m:
        print("No minimax model found in config")
        return
    
    print(f"Testing: {m.get('model_display_name', m.get('model'))}")
    
    r = await run_model(m)
    print(f"Result: {'OK' if r.success else 'FAIL'} {r.source} {r.latency_ms:.0f}ms {r.error}")


if __name__ == "__main__":
    asyncio.run(main())
