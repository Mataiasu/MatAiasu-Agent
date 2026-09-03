from .core import MatAiasuAgent


def main() -> None:
    agent = MatAiasuAgent()
    print("MatAiasu Agent v0.1.0")
    print("Local-first development agent initialized.")
    while True:
        try:
            objective = input("\nmat> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if objective.lower() in {"exit", "quit"}:
            break
        if not objective:
            continue
        result = agent.inspect(objective)
        print(f"Task: {result.task.id}")
        for step in result.task.steps:
            print(f"  - {step}")
        print(result.task.result)


if __name__ == "__main__":
    main()
