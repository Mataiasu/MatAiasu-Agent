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

## Current version: 0.5.0

Implemented:
- Python 3.11+
- local-first runtime
- persistent JSON memory
- append-only execution history
- project registry
- project technology detection
- workspace boundary policy
- permission-gated filesystem and command execution
- machine-readable tool registry with runtime permission enforcement
- read-only Git inspection tools
- deterministic task planner
- workspace and command validation
- bounded execution/retry loop
- local Ollama client with availability check
- interactive CLI
- Windows packaging and auto-update infrastructure
- CI test workflow
- end-to-end coverage for read, write and command lifecycles
- updater safety coverage

## Security defaults

The default profile is read-only. Write, command and Git permissions are opt-in and independent:

```text
MATAIASU_ALLOW_WRITE=1
MATAIASU_ALLOW_COMMANDS=1
MATAIASU_ALLOW_GIT=1
```

Workspace paths are constrained when a `WorkspacePolicy` is used. Unknown tools are rejected and model output cannot grant capabilities. An explicitly empty permission set grants no permissions.

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

`/run` is blocked unless `MATAIASU_ALLOW_COMMANDS=1` is set.

## Project integration contract

A controlled project is a workspace plus metadata. The Agent communicates through generic project information and tool operations; project-specific logic belongs in the project itself. This keeps MatAiasu 3D and Infinite Ascension independent from the Agent core.

For a new project, register its workspace, inspect it, then use the permissioned tools for changes and validation.

## Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest -q
python -m agent.cli
```

Optional environment variables are documented in `.env.example`.
