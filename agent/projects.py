from __future__ import annotations

import json
from pathlib import Path

from .models import Project


class ProjectRegistry:
    """Registry of projects the agent is allowed to operate on."""

    def __init__(self, data_dir: Path) -> None:
        self.path = data_dir / "projects.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[Project]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Project(**item) for item in raw]

    def save(self, projects: list[Project]) -> None:
        payload = [
            {
                "name": p.name,
                "path": p.path,
                "description": p.description,
                "active": p.active,
                "metadata": p.metadata,
            }
            for p in projects
        ]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, project: Project) -> None:
        projects = self.list()
        if any(p.name.lower() == project.name.lower() for p in projects):
            raise ValueError(f"Project already exists: {project.name}")
        projects.append(project)
        self.save(projects)
