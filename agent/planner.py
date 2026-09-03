from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Plan:
    objective: str
    steps: tuple[str, ...]


class TaskPlanner:
    """Produces a safe baseline plan before model-assisted execution."""

    def build(self, objective: str, has_workspace: bool = False) -> Plan:
        objective = objective.strip()
        if not objective:
            raise ValueError("Objective cannot be empty")
        steps = [
            "Understand the requested outcome",
            "Inspect the target project",
            "Determine the smallest safe change",
            "Check required permissions",
            "Execute the approved action",
            "Validate the result",
            "Report what actually happened",
        ]
        if not has_workspace:
            steps[1] = "Identify the target workspace"
        return Plan(objective, tuple(steps))
