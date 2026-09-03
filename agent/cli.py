from __future__ import annotations

import os
import sys

from .core import MatAiasuAgent
from .ollama import OllamaError
from .updater import check_update, launch_update

VERSION = "0.3.0"


def _auto_update() -> None:
    if os.getenv("MATAIASU_AGENT_AUTO_UPDATE", "1").lower() in {"0", "false", "no"}:
        return
    if "--updated-from" in sys.argv:
        return
    result = check_update(VERSION)
    if not result:
        return
    version, url = result
    if launch_update(url, version):
        print(f"Mise à jour {version} détectée. Installation en cours...")
        raise SystemExit(0)


def main() -> None:
    _auto_update()
    agent = MatAiasuAgent()
    print(f"MatAiasu Agent v{VERSION}")
    print("Local-first development agent initialized.")
    print("Commands: /status, /scan <path>, /execute-readonly <path>, /ask <prompt>, /update, exit")
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
            print(f"Version: {VERSION}")
            print(f"Ollama: {'available' if agent.local_model_status() else 'unavailable'}")
            print(f"Model: {agent.settings.model_name}")
            continue
        if line == "/update":
            result = check_update(VERSION)
            if not result:
                print("Aucune mise à jour disponible.")
                continue
            version, url = result
            if launch_update(url, version):
                print(f"Mise à jour {version} en cours...")
                break
            print("La mise à jour nécessite une version Windows packagée.")
            continue
        if line.startswith("/execute-readonly "):
            result = agent.execute_readonly("inspect workspace", line[18:].strip())
            print(f"Task: {result.task.id}")
            print(f"Status: {result.task.status.value}")
            print(result.task.result)
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
