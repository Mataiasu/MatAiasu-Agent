# MatAiasu Agent

Local-first development agent designed to operate MatAiasu projects without being coupled to any single project.

## Vision

MatAiasu Agent is the central development brain. Projects such as **MatAiasu 3D** and **Infinite Ascension** are registered workspaces, not dependencies of the agent.

```text
User request
    ↓
MatAiasu Agent
    ├── Memory
    ├── Planner
    ├── Permissions
    ├── Tools
    ├── Project Registry
    └── History
    ↓
Inspect → Plan → Execute → Test → Report → Git
```

## Current MVP

- Python 3.11+
- local-first runtime
- persistent JSON memory
- project registry
- permission gate
- filesystem tool
- shell execution tool
- task/event domain model
- CLI
- Ollama-ready configuration

The execution core is deliberately conservative at this stage: planning is enabled, while autonomous write/command permissions are not granted by default.

## Planned modules

- Ollama model adapter
- structured planner and tool-calling loop
- Git/GitHub integration
- project scanner and codebase understanding
- durable task/history database
- Windows desktop interface
- optional web/mobile interface
- approval UI for sensitive operations
- test/repair loop
- plugin system

## Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m agent.cli
```

Type `exit` to stop the CLI.
