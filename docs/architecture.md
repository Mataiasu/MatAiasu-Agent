# Architecture

## Principle

The agent is independent from every project it controls. A project is a workspace plus metadata and permissions.

## Layers

### Core

Coordinates requests, tasks, planning, execution and reporting.

### Memory

Stores durable project/user decisions, task history and useful observations. The MVP uses JSON; the long-term implementation should move to SQLite with indexed retrieval.

### Project Registry

Defines which workspaces exist and which one is active. The agent must inspect a workspace before changing it.

### Tools

Tools are explicit capabilities: filesystem, shell, Git/GitHub, tests, build systems and later model/tool adapters.

### Permissions

Read-only is the default. Writing files, executing commands, Git operations and network access require explicit capabilities.

## Execution loop

1. Understand the request.
2. Identify the target project.
3. Inspect the actual workspace.
4. Produce a plan.
5. Ask for/verify required permissions.
6. Execute the smallest safe change.
7. Run relevant tests/builds.
8. Repair failures when permitted.
9. Record the result in history/memory.
10. Present a concise report.

## Model strategy

Ollama is the default local model provider. The model layer must remain replaceable so the agent can later support remote models without coupling the core to a provider.

## Security direction

Never grant arbitrary shell, filesystem or network access merely because the model requests it. Tool calls pass through the permission layer, and sensitive operations should eventually require interactive approval.
