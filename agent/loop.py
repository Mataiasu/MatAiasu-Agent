from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class LoopResult:
    success: bool
    attempts: int
    message: str


class AgentLoop:
    """Generic bounded plan/execute/validate/retry loop."""

    def run(
        self,
        execute: Callable[[int], object],
        validate: Callable[[object], tuple[bool, str]],
        max_attempts: int = 2,
    ) -> LoopResult:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        last_message = "No attempt executed"
        for attempt in range(1, max_attempts + 1):
            result = execute(attempt)
            ok, message = validate(result)
            last_message = message
            if ok:
                return LoopResult(True, attempt, message)
        return LoopResult(False, max_attempts, last_message)
