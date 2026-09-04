# Git access

MatAiasu Agent treats Git as a first-class project tool.

## Capabilities

When Git permission is enabled, the Agent may inspect a repository and perform repository changes through the controlled Git tool layer. Read operations include repository root, current HEAD, status, and diff. Write operations are intended to cover staging, commits, branch operations, and synchronization with a configured remote.

## Safety

Git access is permission-gated. Git operations must remain scoped to the active project workspace. Destructive operations such as force pushes, hard resets, and deleting branches are not part of the default autonomous workflow and require an explicit future safety policy.

The Agent should inspect changes before committing, run validation when appropriate, and record Git actions in its history.
