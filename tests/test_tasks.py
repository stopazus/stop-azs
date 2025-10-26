from pathlib import Path
import json

import pytest

from stop_azs import scan_icloud_tasks, search_tasks


def _write_task(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_scan_applies_defaults(tmp_path: Path) -> None:
    defaults = {"status": "todo", "description": "Pending details", "due_date": "2024-01-01"}
    task_dir = tmp_path / "icloud" / "tasks"
    task_dir.mkdir(parents=True)
    _write_task(task_dir / "task1.json", {"title": "Follow up"})

    tasks = scan_icloud_tasks(task_dir, defaults=defaults)
    assert len(tasks) == 1
    task = tasks[0]
    assert task.status == "todo"
    assert task.description == "Pending details"
    assert task.due_date == "2024-01-01"
    assert task.source == task_dir / "task1.json"


def test_scan_preserves_existing_fields(tmp_path: Path) -> None:
    task_dir = tmp_path / "icloud"
    task_dir.mkdir()
    _write_task(
        task_dir / "task2.json",
        {
            "title": "Complete report",
            "status": "in-progress",
            "description": "Finish quarterly review",
            "due_date": "2024-06-01",
            "category": "finance",
        },
    )

    tasks = scan_icloud_tasks(task_dir)
    assert len(tasks) == 1
    task = tasks[0]
    assert task.status == "in-progress"
    assert task.description == "Finish quarterly review"
    assert task.due_date == "2024-06-01"
    assert task.metadata["category"] == "finance"


def test_scan_errors_when_directory_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan_icloud_tasks(tmp_path / "missing")


def test_scan_errors_on_invalid_json(tmp_path: Path) -> None:
    task_dir = tmp_path / "icloud"
    task_dir.mkdir()
    (task_dir / "broken.json").write_text("not json", encoding="utf-8")

    with pytest.raises(ValueError):
        scan_icloud_tasks(task_dir)


def test_search_returns_matching_tasks(tmp_path: Path) -> None:
    task_dir = tmp_path / "icloud"
    task_dir.mkdir()
    _write_task(
        task_dir / "task3.json",
        {"title": "Call agency", "description": "Contact FBI team"},
    )
    _write_task(
        task_dir / "task4.json",
        {"title": "File reports", "metadata": {"agency": "FinCEN"}},
    )

    tasks = scan_icloud_tasks(task_dir)
    matches = search_tasks(tasks, "fbi")
    assert [task.title for task in matches] == ["Call agency"]

    matches = search_tasks(tasks, "FinCEN")
    assert [task.title for task in matches] == ["File reports"]


def test_search_requires_non_empty_query(tmp_path: Path) -> None:
    task_dir = tmp_path / "icloud"
    task_dir.mkdir()
    _write_task(task_dir / "task.json", {"title": "Dummy"})

    tasks = scan_icloud_tasks(task_dir)
    with pytest.raises(ValueError):
        search_tasks(tasks, "   ")
