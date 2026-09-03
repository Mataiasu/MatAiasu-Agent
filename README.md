# MatAiasu Agent

Local-first development agent designed to operate multiple MatAiasu projects without being coupled to any single project.

## Architecture

```text
User
  ↓
MatAiasu Agent
  ├─ Core / task orchestration
  ├─ Local model (Ollama)
  ├─ Memory + append-only history
  ├─ Project registry
  ├─ Read-only workspace scanner
  ├─ Permission gate
  └─ Tools (filesystem / shell / Git / tests)
  ↓
Selected project
```

Projects are workspaces, not dependencies. The Agent must inspect a workspace before changing it.

## Safety model

Read access is the default. Model output never grants permissions. File writes, command execution, Git operations and network access remain gated capabilities and will require explicit approval before autonomous execution is enabled.

## Current version: 0.2.0

Implemented:
- Python 3.11+
- local-first runtime
- persistent JSON memory
- append-only execution history
- project registry
- permission gate
- read-only workspace scanner
- filesystem and shell tool foundations
- local Ollama client with availability check
- interactive CLI with `/status`, `/scan` and `/ask`
- CI test workflow

## Next milestones

1. Structured planner with machine-readable actions
2. Tool registry and approval workflow
3. Git integration and safe diff/rollback
4. Automatic project detection and codebase summaries
5. Test/build/repair loop
6. SQLite memory and task history
7. Windows desktop application
8. Optional web/mobile client
9. Plugin system

## Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m agent.cli
```

Optional environment variables are documented in `.env.example`.
