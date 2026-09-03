from .core import MatAiasuAgent
from .ollama import OllamaError


def main() -> None:
    agent = MatAiasuAgent()
    print("MatAiasu Agent v0.2.0")
    print("Local-first development agent initialized.")
    print("Commands: /status, /scan <path>, /ask <prompt>, exit")
    while True:
        try:
            line = input("\nmat> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in {"exit", "quit"}:
            break
        if not line:
            continue
        if line == "/status":
            print(f"Ollama: {'available' if agent.local_model_status() else 'unavailable'}")
            print(f"Model: {agent.settings.model_name}")
            continue
        if line.startswith("/scan "):
            try:
                result = agent.scan_workspace(line[6:].strip())
                print(f"Workspace: {result['root']}")
                print(f"Files: {result['file_count']}")
                print(f"Extensions: {result['extensions']}")
            except (OSError, ValueError) as exc:
                print(f"Scan error: {exc}")
            continue
        if line.startswith("/ask "):
            try:
                print(agent.ask_local_model(line[5:].strip()))
            except OllamaError as exc:
                print(exc)
            continue
        result = agent.inspect(line)
        print(f"Task: {result.task.id}")
        for step in result.task.steps:
            print(f"  - {step}")
        print(result.task.result)


if __name__ == "__main__":
    main()
