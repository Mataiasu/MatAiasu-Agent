# MatAiasu Agent

Local-first development agent designed to operate multiple MatAiasu projects without being coupled to any single project.

## Architecture

```text
User
  ↓
MatAiasu Agent
  ├─ Core / task orchestration
  ├─ Planner
  ├─ Bounded execution loop
  ├─ Local model (Ollama)
  ├─ Memory + append-only history
  ├─ Project registry
  ├─ Read-only workspace scanner
  ├─ Permission gate
  ├─ Validator
  └─ Tools (filesystem / shell / Git / tests)
  ↓
Selected project
```

Projects are workspaces, not dependencies. The Agent inspects a workspace before changing it. The model never receives implicit authority: every real tool operation passes through the permission layer.

## Safety model

Read access is the default. Model output never grants permissions. File writes, command execution, Git operations and network access remain gated capabilities. Autonomous execution is bounded and validation-driven.

## Current version: 0.3.0

Implemented:
- Python 3.11+
- local-first runtime
- persistent JSON memory
- append-only execution history
- project registry
- permission gate
- read-only workspace scanner
- filesystem and shell tool foundations
- permission-aware executor
- deterministic task planner
- workspace and command validation
- bounded retry loop
- local Ollama client with availability check
- interactive CLI with `/status`, `/scan`, `/execute-readonly`, `/ask` and `/update`
- Windows packaging and auto-update infrastructure
- CI test workflow

## Roadmap

1. Machine-readable tool registry and approval workflow
2. Git integration with diff, checkpoint and rollback
3. Automatic project detection and codebase summaries
4. Test/build/repair orchestration
5. SQLite-backed memory and task history
6. Windows desktop interface
7. Optional web/mobile client
8. Plugin system

## Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m agent.cli
```

Optional environment variables are documented in `.env.example`.
