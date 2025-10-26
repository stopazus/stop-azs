"""Utilities for working with task files sourced from an iCloud Drive folder."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json


@dataclass
class Task:
    """Representation of a single task entry."""

    title: str
    description: str = ""
    status: str = "pending"
    due_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[Path] = None

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        *,
        defaults: Optional[Dict[str, Any]] = None,
        source: Optional[Path] = None,
    ) -> "Task":
        """Create a task from a raw dictionary, applying defaults when fields are missing."""

        if not isinstance(data, dict):
            raise ValueError("Task data must be a dictionary")

        defaults = defaults or {}

        def _get(key: str, fallback: Any) -> Any:
            value = data.get(key)
            if value in (None, "", []):
                return defaults.get(key, fallback)
            return value

        title = data.get("title") or defaults.get("title")
        if not title:
            raise ValueError("Task is missing a title")

        description = _get("description", "")
        status = _get("status", "pending")
        due_date = _get("due_date", None)

        metadata = {
            key: value
            for key, value in data.items()
            if key not in {"title", "description", "status", "due_date"}
        }

        return cls(
            title=title,
            description=description,
            status=status,
            due_date=due_date,
            metadata=metadata,
            source=source,
        )

    def matches(self, query: str) -> bool:
        """Return ``True`` if the query string appears in the task fields."""

        query_lower = query.lower()
        if query_lower in self.title.lower() or query_lower in self.description.lower():
            return True
        return any(
            query_lower in str(value).lower()
            for value in self.metadata.values()
        )


def _iter_task_files(base_path: Path) -> Iterable[Path]:
    """Yield candidate task files within the provided directory."""

    for path in base_path.rglob("*.json"):
        if path.is_file():
            yield path


def _load_raw_task(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in task file {path}") from exc


def scan_icloud_tasks(
    base_path: Path | str,
    *,
    defaults: Optional[Dict[str, Any]] = None,
) -> List[Task]:
    """Scan ``base_path`` for task files and return a list of :class:`Task` objects."""

    directory = Path(base_path)
    if not directory.exists():
        raise FileNotFoundError(f"Task directory '{directory}' does not exist")
    if not directory.is_dir():
        raise NotADirectoryError(f"Task directory '{directory}' is not a directory")

    tasks: List[Task] = []
    for file_path in _iter_task_files(directory):
        raw = _load_raw_task(file_path)
        task = Task.from_dict(raw, defaults=defaults, source=file_path)
        tasks.append(task)
    return tasks


def search_tasks(tasks: Iterable[Task], query: str) -> List[Task]:
    """Return tasks whose fields contain the provided query string."""

    query = query.strip()
    if not query:
        raise ValueError("Query string cannot be empty")

    return [task for task in tasks if task.matches(query)]
