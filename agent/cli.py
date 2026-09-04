from __future__ import annotations

import os
import shlex
import sys

from .core import MatAiasuAgent
from .ollama import OllamaError
from .updater import check_update, launch_update

VERSION = "0.5.0"


def _auto_update() -> None:
    if os.getenv("MATAIASU_AGENT_AUTO_UPDATE", "1").lower() in {"0", "false", "no"} or "--updated-from" in sys.argv:
        return
    result = check_update(VERSION)
    if result:
        version, url = result
        if launch_update(url, version):
            print(f"Mise à jour {version} détectée. Installation en cours...")
            raise SystemExit(0)


def main() -> None:
    _auto_update()
    agent = MatAiasuAgent()
    print(f"MatAiasu Agent v{VERSION}")
    print("Local-first development agent initialized.")
    print("Commands: /status, /tools, /detect <path>, /scan <path>, /agent <workspace> <task>, /execute-readonly <path>, /run <workspace> <command...>, /ask <prompt>, /update, exit")
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
            print(f"Write permission: {agent.settings.allow_write}")
            print(f"Command permission: {agent.settings.allow_commands}")
            print(f"Git permission: {agent.settings.allow_git}")
            continue
        if line == "/tools":
            for tool in agent.available_tools():
                print(f"- {tool['name']}: {tool['description']} [{tool['permission']}]")
            continue
        if line.startswith("/detect "):
            try:
                result = agent.detect_project(line[8:].strip())
                print(f"Types: {', '.join(result['types'])}")
                print(f"Primary: {result['primary_type']}")
                print(f"Markers: {result['markers']}")
            except (OSError, ValueError) as exc:
                print(f"Detection error: {exc}")
            continue
        if line == "/update":
            result = check_update(VERSION)
            if not result:
                print("Aucune mise à jour disponible.")
            else:
                version, url = result
                if launch_update(url, version):
                    print(f"Mise à jour {version} en cours...")
                    break
                print("La mise à jour nécessite une version Windows packagée.")
            continue
        if line.startswith("/agent "):
            try:
                parts = shlex.split(line[7:].strip())
            except ValueError as exc:
                print(f"Agent parsing error: {exc}")
                continue
            if len(parts) < 2:
                print("Usage: /agent <workspace> <task>")
                continue
            workspace = parts[0]
            objective = " ".join(parts[1:])
            try:
                result = agent.run_agent_task(objective, workspace)
                print(f"Task: {result.task.id}\nStatus: {result.task.status.value}\n{result.task.result}")
                print(f"Events: {len(result.events)}")
            except OllamaError as exc:
                print(f"Ollama error: {exc}")
            continue
        if line.startswith("/execute-readonly "):
            result = agent.execute_readonly("inspect workspace", line[18:].strip())
            print(f"Task: {result.task.id}\nStatus: {result.task.status.value}\n{result.task.result}")
            continue
        if line.startswith("/run "):
            try:
                parts = shlex.split(line[5:].strip())
            except ValueError as exc:
                print(f"Command parsing error: {exc}")
                continue
            if len(parts) < 2:
                print("Usage: /run <workspace> <command...>")
                continue
            result = agent.execute_command_task("run requested command", parts[1:], parts[0])
            print(f"Task: {result.task.id}\nStatus: {result.task.status.value}\n{result.task.result}")
            continue
        if line.startswith("/scan "):
            try:
                result = agent.scan_workspace(line[6:].strip())
                print(f"Workspace: {result['root']}\nFiles: {result['file_count']}\nExtensions: {result['extensions']}")
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
