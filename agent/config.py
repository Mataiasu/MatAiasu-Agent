from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass(slots=True)
class Settings:
    """Runtime configuration. Environment variables override defaults."""

    data_dir: Path = field(default_factory=lambda: Path(os.getenv("MATAIASU_DATA_DIR", ".data")))
    model_provider: str = field(default_factory=lambda: os.getenv("MATAIASU_MODEL_PROVIDER", "ollama"))
    model_name: str = field(default_factory=lambda: os.getenv("MATAIASU_MODEL_NAME", "qwen3"))
    ollama_url: str = field(default_factory=lambda: os.getenv("MATAIASU_OLLAMA_URL", "http://127.0.0.1:11434"))
    workspace_root: Path = field(default_factory=lambda: Path(os.getenv("MATAIASU_WORKSPACE", ".")))

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "projects").mkdir(exist_ok=True)
        (self.data_dir / "memory").mkdir(exist_ok=True)
        (self.data_dir / "logs").mkdir(exist_ok=True)
