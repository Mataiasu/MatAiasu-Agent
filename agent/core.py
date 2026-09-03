from dataclasses import dataclass
from uuid import uuid4

from .config import Settings
from .memory.store import MemoryStore
from .models import Event, Task, TaskStatus
from .permissions import PermissionManager
from .projects import ProjectRegistry


@dataclass(slots=True)
class AgentResult:
    task: Task
    events: list[Event]


class MatAiasuAgent:
    """Orchestration core. Model adapters and autonomous planning plug into this layer."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.settings.ensure_dirs()
        self.memory = MemoryStore(self.settings.data_dir)
        self.projects = ProjectRegistry(self.settings.data_dir)
        self.permissions = PermissionManager()

    def create_task(self, objective: str, project: str | None = None) -> Task:
        if not objective.strip():
            raise ValueError("Objective cannot be empty")
        return Task(id=str(uuid4()), objective=objective.strip(), project=project)

    def inspect(self, objective: str, project: str | None = None) -> AgentResult:
        task = self.create_task(objective, project)
        task.status = TaskStatus.RUNNING
        events = [Event("task.created", objective, {"task_id": task.id})]
        task.steps = [
            "Inspect the selected project and constraints",
            "Build an execution plan",
            "Request only the permissions required",
            "Execute changes",
            "Run validation/tests",
            "Report results and preserve history",
        ]
        task.status = TaskStatus.DONE
        task.result = "Planning skeleton created; execution adapters are intentionally not enabled yet."
        events.append(Event("task.planned", task.result, {"task_id": task.id}))
        return AgentResult(task, events)
