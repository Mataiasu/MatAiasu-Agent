import json
from pathlib import Path
from typing import Any


class MemoryStore:
    """Small JSON-backed persistent memory for the MVP."""

    def __init__(self, root: Path) -> None:
        self.path = root / "memory" / "memory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def add(self, content: str, kind: str = "note", metadata: dict[str, Any] | None = None) -> None:
        items = self.load()
        items.append({"kind": kind, "content": content, "metadata": metadata or {}})
        self.path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        terms = {term.lower() for term in query.split() if term.strip()}
        scored = []
        for item in self.load():
            text = item.get("content", "").lower()
            score = sum(term in text for term in terms)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]
