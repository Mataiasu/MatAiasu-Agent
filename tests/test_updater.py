from pathlib import Path
import zipfile

import pytest

from agent.updater import _safe_extract, _version, check_update


def test_version_parser_handles_v_prefix() -> None:
    assert _version("v0.5.0") == (0, 5, 0)
    assert _version("0.4.0") < _version("0.5.0")


def test_safe_extract_rejects_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "update.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../escape.txt", "bad")

    with zipfile.ZipFile(archive) as bundle:
        with pytest.raises(ValueError):
            _safe_extract(bundle, tmp_path / "out")


def test_check_update_returns_none_when_release_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("agent.updater.latest_release", lambda: None)
    assert check_update("0.5.0") is None
