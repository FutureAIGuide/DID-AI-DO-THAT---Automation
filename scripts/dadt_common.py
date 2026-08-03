"""Shared helpers for DADT GitHub Actions automation.

This module centralizes the OpenRouter client and file/report helpers that
were previously duplicated inline across daily-discovery.yml,
story-production.yml, and publish-pipeline.yml. Consolidating them here:

- makes the retry/backoff and cost-guard logic consistent across workflows
- lets us unit test the pure parsing/formatting helpers with pytest
- shrinks each workflow's embedded Python to just its business logic

Workflows import this module by adding the checked-out `scripts/` directory
to `sys.path` before importing, e.g.:

    import sys, pathlib
    root = pathlib.Path(os.environ["GITHUB_WORKSPACE"])
    sys.path.insert(0, str(root / "scripts"))
    import dadt_common as dc
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"
DEFAULT_MAX_TOKENS = 8000
DEFAULT_TIMEOUT_SECONDS = 300
DEFAULT_MAX_RETRIES = 4
RETRYABLE_HTTP_STATUS = {408, 429, 500, 502, 503, 504}

SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class OpenRouterError(RuntimeError):
    """Raised when an OpenRouter call fails after all retries."""


def is_valid_slug(slug: str) -> bool:
    return bool(re.fullmatch(SLUG_PATTERN, slug or ""))


def render_text(content) -> str:
    """Normalize an OpenRouter message `content` field to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


@dataclass
class OpenRouterClient:
    api_key: str
    model: str = DEFAULT_MODEL
    referer: str = ""
    title: str = "DID AI DO THAT?! Automation"
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = 0.2
    system_prompt: str = (
        "You are an evidence-first automation agent for the DID AI DO THAT?! "
        "repository. Never fabricate sources, citations, dates, people, "
        "organizations, statistics, or legal claims. Return markdown only "
        "unless JSON is explicitly requested."
    )
    sleep_fn: Callable[[float], None] = field(default=time.sleep, repr=False)

    def call(self, label: str, prompt: str, max_tokens: int | None = None) -> str:
        """Call OpenRouter with retry + exponential backoff on transient errors."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json",
        }
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.title:
            headers["X-Title"] = self.title

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            request = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                choices = body.get("choices") or []
                if not choices:
                    raise OpenRouterError(f"OpenRouter returned no choices during {label}: {body}")
                return render_text(choices[0]["message"]["content"]).strip()
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                last_error = OpenRouterError(f"OpenRouter request failed during {label}: {exc.code} {detail}")
                if exc.code not in RETRYABLE_HTTP_STATUS or attempt == self.max_retries:
                    raise last_error from exc
            except urllib.error.URLError as exc:
                last_error = OpenRouterError(f"OpenRouter request failed during {label}: {exc}")
                if attempt == self.max_retries:
                    raise last_error from exc
            backoff = min(2 ** attempt, 30)
            self.sleep_fn(backoff)
        # Unreachable in practice, but keeps type-checkers happy.
        raise last_error or OpenRouterError(f"OpenRouter request failed during {label}")


def next_file(root: Path, rel: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    index = 2
    while True:
        candidate = path.with_name(f"{stem}-{index:02d}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def next_dir(root: Path, rel: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.parent / f"{path.name}-{index:02d}"
        if not candidate.exists():
            return candidate
        index += 1


def save_file(root: Path, rel: str, content: str) -> Path:
    path = next_file(root, rel)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def split_sections(content: str, headings: list[str]) -> dict[str, str]:
    """Split a markdown document into `# HEADING` sections, keyed uppercase."""
    pattern = re.compile(r"^#\s+(.+?)\s*$", flags=re.MULTILINE)
    matches = list(pattern.finditer(content))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        heading = match.group(1).strip().upper()
        sections[heading] = content[start:end].strip()
    missing = [heading for heading in headings if heading not in sections]
    if missing:
        raise ValueError(f"Expected sections not found: {', '.join(missing)}")
    return sections


def parse_decision(report_text: str) -> str:
    """Extract PUBLISH/HOLD/REJECT from a verification report."""
    final_line = re.search(
        r"^FINAL DECISION:\s*(PUBLISH|HOLD|REJECT)\s*$",
        report_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if final_line:
        return final_line.group(1).upper()
    matches = re.findall(r"\b(PUBLISH|HOLD|REJECT)\b", report_text.upper())
    if not matches:
        raise ValueError("Could not determine verification decision from report output.")
    return matches[-1]


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
