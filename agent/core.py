from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .config import Settings
from .executor import AgentExecutor
from .history import HistoryStore
from .loop import AgentLoop
from .memory.store import MemoryStore
from .models import Event, Task, TaskStatus
from .ollama import OllamaClient
from .permissions import Permission, PermissionManager
from .planner import TaskPlanner
from .projects import ProjectRegistry
from .tools.files import FileTool
from .tools.policy import WorkspacePolicy
from .tools.shell import ShellTool
from .tools.workspace import WorkspaceScanner
from .validator import Validator


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
        grants = {Permission.READ_FILES}
        if self.settings.allow_write:
            grants.add(Permission.WRITE_FILES)
        if self.settings.allow_commands:
            grants.add(Permission.RUN_COMMANDS)
        self.permissions = PermissionManager(grants)
        self.scanner = WorkspaceScanner()
        self.files = FileTool()
        self.shell = ShellTool()
        self.executor = AgentExecutor(self.permissions, self.files, self.shell)
        self.planner = TaskPlanner()
        self.validator = Validator(self.scanner)
        self.loop = AgentLoop()
        self.model = OllamaClient(self.settings.ollama_url, self.settings.model_name)

    def create_task(self, objective: str, project: str | None = None) -> Task:
        if not objective.strip():
            raise ValueError("Objective cannot be empty")
        return Task(id=str(uuid4()), objective=objective.strip(), project=project)

    def inspect(self, objective: str, project: str | None = None) -> AgentResult:
        task = self.create_task(objective, project)
        task.status = TaskStatus.RUNNING
        events = [Event("task.created", objective, {"task_id": task.id})]
        plan = self.planner.build(objective, has_workspace=project is not None)
        task.steps = list(plan.steps)
        task.status = TaskStatus.DONE
        task.result = "Planning completed; no write or command permission was used."
        self.history.append("task.planned", {"task_id": task.id, "objective": task.objective, "steps": task.steps})
        events.append(Event("task.planned", task.result, {"task_id": task.id, "steps": task.steps}))
        return AgentResult(task, events)

    def execute_readonly(self, objective: str, root: str | Path) -> AgentResult:
        """Run a real, read-only task: plan, scan, validate and persist the result."""
        task = self.create_task(objective)
        task.status = TaskStatus.RUNNING
        events = [Event("task.created", objective, {"task_id": task.id})]
        try:
            policy = WorkspacePolicy(Path(root))
            self.permissions.require(Permission.READ_FILES)
            plan = self.planner.build(objective, has_workspace=True)
            task.steps = list(plan.steps)
            scan = self.scanner.scan(policy.root)
            validation = self.validator.workspace(policy.root)
            if not validation.ok:
                raise ValueError(validation.message)
            task.status = TaskStatus.DONE
            task.result = f"{validation.message} | extensions: {scan['extensions']}"
            events.extend([
                Event("workspace.scanned", task.result, scan),
                Event("task.validated", validation.message, {"ok": validation.ok}),
            ])
            self.memory.add(task.result, kind="execution")
            self.history.append("task.completed", {"task_id": task.id, "result": task.result})
        except (OSError, ValueError, PermissionError) as exc:
            task.status = TaskStatus.BLOCKED if isinstance(exc, PermissionError) else TaskStatus.FAILED
            task.result = str(exc)
            events.append(Event("task.failed", task.result, {"task_id": task.id}))
            self.history.append("task.failed", {"task_id": task.id, "error": task.result})
        return AgentResult(task, events)

    def write_file(self, path: str | Path, content: str, workspace: str | Path | None = None) -> None:
        """Controlled write entry point with an optional workspace boundary."""
        policy = WorkspacePolicy(Path(workspace)) if workspace else None
        self.executor.write_file(Path(path), content, policy)
        self.history.append("file.written", {"path": str((policy.resolve(Path(path)) if policy else Path(path)).resolve())})

    def run_command(self, command: list[str], cwd: str | Path, timeout: int = 120) -> tuple[int, str, str]:
        """Controlled command entry point; permission is checked immediately before execution."""
        policy = WorkspacePolicy(Path(cwd))
        result = self.executor.run_command(command, policy.root, timeout, policy)
        self.history.append("command.executed", {"command": command, "cwd": str(policy.root), "returncode": result[0]})
        return result

    def execute_command_task(self, objective: str, command: list[str], cwd: str | Path, timeout: int = 120) -> AgentResult:
        """Execute one explicit command through the permissioned task lifecycle."""
        task = self.create_task(objective)
        task.status = TaskStatus.RUNNING
        events = [Event("task.created", objective, {"task_id": task.id, "command": command})]
        try:
            policy = WorkspacePolicy(Path(cwd))
            task.steps = list(self.planner.build(objective, has_workspace=True).steps)
            self.permissions.require(Permission.RUN_COMMANDS)
            code, stdout, stderr = self.executor.run_command(command, policy.root, timeout, policy)
            validation = self.validator.command(code, stdout, stderr)
            task.status = TaskStatus.DONE if validation.ok else TaskStatus.FAILED
            task.result = validation.message
            events.append(Event("command.executed", task.result, {"returncode": code}))
            self.history.append("task.completed" if task.status == TaskStatus.DONE else "task.failed", {
                "task_id": task.id, "command": command, "returncode": code, "result": task.result,
            })
        except (OSError, ValueError, PermissionError) as exc:
            task.status = TaskStatus.BLOCKED if isinstance(exc, PermissionError) else TaskStatus.FAILED
            task.result = str(exc)
            events.append(Event("task.failed", task.result, {"task_id": task.id}))
            self.history.append("task.failed", {"task_id": task.id, "error": task.result})
        return AgentResult(task, events)

    def validate_command(self, returncode: int, stdout: str, stderr: str) -> bool:
        return self.validator.command(returncode, stdout, stderr).ok

    def ask_local_model(self, prompt: str) -> str:
        """Ask the configured local model without granting it any tools."""
        return self.model.chat(prompt, system=self.SYSTEM_PROMPT)

    def scan_workspace(self, root: str | Path) -> dict[str, object]:
        """Perform a read-only workspace scan."""
        policy = WorkspacePolicy(Path(root))
        result = self.scanner.scan(policy.root)
        self.history.append("workspace.scanned", result)
        return result

    def local_model_status(self) -> bool:
        return self.model.available()
