from agent.loop import AgentLoop


def test_loop_retries_after_validation_failure() -> None:
    attempts = []

    def execute(attempt: int) -> object:
        attempts.append(attempt)
        return attempt

    def validate(result: object) -> tuple[bool, str]:
        return result == 2, "validated" if result == 2 else "failed"

    result = AgentLoop().run(execute, validate, max_attempts=2)
    assert result.success
    assert result.attempts == 2
    assert attempts == [1, 2]


def test_loop_is_bounded() -> None:
    result = AgentLoop().run(lambda _: None, lambda _: (False, "still failing"), max_attempts=2)
    assert not result.success
    assert result.attempts == 2
