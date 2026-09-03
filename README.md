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
  ├─ Project registry + detector
  ├─ Read-only workspace scanner
  ├─ Permission gate
  ├─ Validator
  └─ Tools (filesystem / shell / Git)
  ↓
Selected project workspace
```

Projects are workspaces, not dependencies. The Agent inspects a workspace before changing it. Model output never grants permissions: every real tool operation passes through the permission layer.

## Current version: 0.4.0

Implemented:
- Python 3.11+
- local-first runtime
- persistent JSON memory
- append-only execution history
- project registry
- project technology detection
- workspace boundary policy
- permission-gated filesystem and command execution
- machine-readable tool registry
- read-only Git inspection tools
- deterministic task planner
- workspace and command validation
- bounded execution/retry loop
- local Ollama client with availability check
- interactive CLI
- Windows packaging and auto-update infrastructure
- CI test workflow

## Security defaults

The default profile is read-only. Write, command and Git permissions are opt-in through environment variables:

```text
MATAIASU_ALLOW_WRITE=1
MATAIASU_ALLOW_COMMANDS=1
MATAIASU_ALLOW_GIT=1
```

These permissions are independent. Enabling commands does not automatically enable writes or Git. Workspace paths are still constrained when a `WorkspacePolicy` is used.

## CLI

```text
/status
/tools
/detect <path>
/scan <path>
/execute-readonly <path>
/run <workspace> <command...>
/ask <prompt>
/update
```

`/run` remains blocked unless `MATAIASU_ALLOW_COMMANDS=1` is set. The agent never treats model-generated text as permission to execute a command.

## Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m agent.cli
```

Optional environment variables are documented in `.env.example`.
