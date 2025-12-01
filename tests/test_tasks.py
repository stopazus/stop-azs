import json
import os
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_restore_creates_default_dataset(tmp_path: Path) -> None:
    from sar_parser.tasks import DEFAULT_TASKS, restore_onedrive_tasks

    destination = tmp_path / "onedrive_tasks.json"
    created_path = restore_onedrive_tasks(destination)

    assert created_path == destination
    assert created_path.exists()

    data = json.loads(created_path.read_text(encoding="utf-8"))
    assert len(data) == len(DEFAULT_TASKS)
    assert {item["task_id"] for item in data} == {task.task_id for task in DEFAULT_TASKS}


def test_restore_does_not_overwrite_existing(tmp_path: Path) -> None:
    from sar_parser.tasks import restore_onedrive_tasks

    destination = tmp_path / "onedrive_tasks.json"
    destination.write_text("[]", encoding="utf-8")

    restore_onedrive_tasks(destination)
    assert destination.read_text(encoding="utf-8") == "[]"

    restore_onedrive_tasks(destination, overwrite=True)
    assert destination.read_text(encoding="utf-8").strip().startswith("[")


def test_restore_supports_paths_with_spaces(tmp_path: Path) -> None:
    """Ensure restoration works for destinations containing spaces."""

    from sar_parser.tasks import DEFAULT_TASKS, restore_onedrive_tasks

    destination = tmp_path / "SSD V7 2TB" / "workspace" / "data" / "onedrive_tasks.json"

    created_path = restore_onedrive_tasks(destination)

    assert created_path == destination
    assert created_path.exists()

    data = json.loads(created_path.read_text(encoding="utf-8"))
    assert len(data) == len(DEFAULT_TASKS)
    assert {item["task_id"] for item in data} == {task.task_id for task in DEFAULT_TASKS}


def test_load_restores_missing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from sar_parser import tasks as tasks_module

    target = tmp_path / "tasks.json"
    monkeypatch.setattr(tasks_module, "DEFAULT_TASKS_FILE", target)

    loaded = tasks_module.load_onedrive_tasks()
    assert target.exists()
    assert all(task.task_id.startswith("onedrive-") for task in loaded)


def test_iter_helper_returns_iterator() -> None:
    from sar_parser.tasks import iter_onedrive_tasks

    iterator = iter_onedrive_tasks()
    assert iter(iterator) is iterator


def test_task_from_dict_requires_fields() -> None:
    from sar_parser.tasks import Task

    with pytest.raises(ValueError, match="missing required fields: status"):
        Task.from_dict({
            "task_id": "onedrive-missing",
            "title": "Incomplete payload",
            "assignee": "qa",
        })
