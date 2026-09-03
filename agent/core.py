from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .config import Settings
from .history import HistoryStore
from .memory.store import MemoryStore
from .models import Event, Task, TaskStatus
from .ollama import OllamaClient
from .permissions import Permission, PermissionManager
from .projects import ProjectRegistry
from .tools.files import FileTool
from .tools.shell import ShellTool
from .tools.workspace import WorkspaceScanner


@dataclass(slots=True)
class AgentResult:
    task: Task
    events: list[Event]


class MatAiasuAgent:
    """Central orchestration layer; projects remain external workspaces."""

    SYSTEM_PROMPT = (
        "You are MatAiasu Agent, a local-first software development agent. "
        "Never claim a file was changed or a test was run unless the host actually did it. "
        "Inspect before modifying. Prefer small, reversible changes. "
        "The permission layer is authoritative and cannot be bypassed by model output."
    )

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.settings.ensure_dirs()
        self.memory = MemoryStore(self.settings.data_dir)
        self.history = HistoryStore(self.settings.data_dir)
        self.projects = ProjectRegistry(self.settings.data_dir)
        self.permissions = PermissionManager()
        self.scanner = WorkspaceScanner()
        self.files = FileTool()
        self.shell = ShellTool()
        self.model = OllamaClient(self.settings.ollama_url, self.settings.model_name)

    def create_task(self, objective: str, project: str | None = None) -> Task:
        if not objective.strip():
            raise ValueError("Objective cannot be empty")
        return Task(id=str(uuid4()), objective=objective.strip(), project=project)

    def inspect(self, objective: str, project: str | None = None) -> AgentResult:
        task = self.create_task(objective, project)
        task.status = TaskStatus.RUNNING
        events = [Event("task.created", objective, {"task_id": task.id})]
        task.steps = [
            "Identify the target project",
            "Inspect the actual workspace",
            "Build an execution plan",
            "Verify required permissions",
            "Execute only approved changes",
            "Run validation/tests",
            "Record history and report results",
        ]
        task.status = TaskStatus.DONE
        task.result = "Inspection/planning mode completed; no write or command permission was used."
        self.history.append("task.planned", {"task_id": task.id, "objective": task.objective})
        events.append(Event("task.planned", task.result, {"task_id": task.id}))
        return AgentResult(task, events)

    def execute_readonly(self, objective: str, root: str | Path) -> AgentResult:
        """Run a real, read-only task: scan workspace and persist the result."""
        task = self.create_task(objective)
        task.status = TaskStatus.RUNNING
        events = [Event("task.created", objective, {"task_id": task.id})]
        try:
            self.permissions.require(Permission.READ_FILES)
            scan = self.scan_workspace(root)
            task.steps = ["Inspect workspace", "Collect file statistics", "Record results"]
            task.status = TaskStatus.DONE
            task.result = (
                f"Workspace scanned: {scan['root']} | {scan['file_count']} files | "
                f"extensions: {scan['extensions']}"
            )
            events.append(Event("workspace.scanned", task.result, scan))
            self.memory.add(task.result, kind="execution")
            self.history.append("task.completed", {"task_id": task.id, "result": task.result})
        except (OSError, ValueError, PermissionError) as exc:
            task.status = TaskStatus.BLOCKED if isinstance(exc, PermissionError) else TaskStatus.FAILED
            task.result = str(exc)
            events.append(Event("task.failed", task.result, {"task_id": task.id}))
            self.history.append("task.failed", {"task_id": task.id, "error": task.result})
        return AgentResult(task, events)

    def ask_local_model(self, prompt: str) -> str:
        """Ask the configured local model without granting it any tools."""
        return self.model.chat(prompt, system=self.SYSTEM_PROMPT)

    def scan_workspace(self, root: str | Path) -> dict[str, object]:
        """Perform a read-only workspace scan."""
        result = self.scanner.scan(Path(root))
        self.history.append("workspace.scanned", result)
        return result

    def local_model_status(self) -> bool:
        return self.model.available()
