from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

REPO_API = "https://api.github.com/repos/Mataiasu/MatAiasu-Agent/releases/latest"
ASSET_NAME = "MatAiasu-Agent-Windows.zip"


def _version(value: str) -> tuple[int, ...]:
    value = value.strip().lstrip("v")
    parts = []
    for part in value.split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        parts.append(int(digits or "0"))
    return tuple(parts[:4])


def latest_release() -> dict | None:
    request = urllib.request.Request(
        REPO_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "MatAiasu-Agent"},
    )
    try:
        with urllib.request.urlopen(request, timeout=4) as response:
            return json.load(response)
    except Exception:
        return None


def check_update(current_version: str) -> tuple[str, str] | None:
    release = latest_release()
    if not release:
        return None
    tag = str(release.get("tag_name", ""))
    if not tag or _version(tag) <= _version(current_version):
        return None
    for asset in release.get("assets", []):
        if asset.get("name") == ASSET_NAME and asset.get("browser_download_url"):
            return tag.lstrip("v"), str(asset["browser_download_url"])
    return None


def launch_update(download_url: str, version: str) -> bool:
    # Never attempt a self-update while running from Python source. In that
    # case sys.executable is python.exe, not MatAiasu-Agent.exe.
    if not getattr(sys, "frozen", False):
        return False

    target = Path(sys.executable).resolve()
    if target.suffix.lower() != ".exe":
        return False

    updater = target.with_name("MatAiasu-Agent-Updater.exe")
    if not updater.exists():
        return False

    subprocess.Popen(
        [str(updater), "--apply", download_url, version, str(target)],
        close_fds=True,
    )
    return True


def _safe_extract(bundle: zipfile.ZipFile, destination: Path) -> None:
    root = destination.resolve()
    for member in bundle.infolist():
        target = (destination / member.filename).resolve()
        if root not in target.parents and target != root:
            raise ValueError("Unsafe path in update archive")
    bundle.extractall(destination)


def apply_update(download_url: str, version: str, target: Path) -> int:
    if os.name != "nt":
        return 1

    temp_root = Path(tempfile.mkdtemp(prefix="mataiasu-agent-update-"))
    archive = temp_root / ASSET_NAME
    extracted = temp_root / "extracted"
    try:
        request = urllib.request.Request(
            download_url,
            headers={"Accept": "application/octet-stream", "User-Agent": "MatAiasu-Agent"},
        )
        with urllib.request.urlopen(request, timeout=60) as response, archive.open("wb") as output:
            shutil.copyfileobj(response, output)
        extracted.mkdir()
        with zipfile.ZipFile(archive) as bundle:
            _safe_extract(bundle, extracted)

        new_exe = next(extracted.rglob(target.name), None)
        if new_exe is None:
            return 2

        backup = target.with_suffix(target.suffix + ".old")
        for _ in range(30):
            try:
                if target.exists():
                    shutil.copy2(target, backup)
                shutil.copy2(new_exe, target)
                break
            except PermissionError:
                time.sleep(0.5)
        else:
            return 3

        subprocess.Popen([str(target), "--updated-from", version], close_fds=True)
        return 0
    except (OSError, ValueError, zipfile.BadZipFile):
        return 4
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", nargs=3, metavar=("URL", "VERSION", "TARGET"))
    args = parser.parse_args()
    if args.apply:
        url, version, target = args.apply
        return apply_update(url, version, Path(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
