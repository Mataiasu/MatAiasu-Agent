import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class HistoryStore:
    """Append-only JSONL execution history."""

    def __init__(self, root: Path) -> None:
        self.path = root / "logs" / "history.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event_type: str, data: dict[str, Any]) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "data": data,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
