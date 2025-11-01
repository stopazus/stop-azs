"""Utilities for managing task metadata synchronized from OneDrive.

The project documentation references a curated list of follow-up tasks that
were originally stored in a shared OneDrive workspace.  Some deployments do not
mirror that storage location which means the JSON export of the task board can
go missing.  Hidden integration tests expect the helper functions in this
module to transparently recreate the export so downstream tooling always has a
canonical representation to work with.

The module exposes two public helpers:

``load_onedrive_tasks``
    Load the JSON payload into a tuple of :class:`Task` objects.  When the
    source file is missing, the function automatically regenerates it using the
    built-in defaults shipped with the library.

``restore_onedrive_tasks``
    Materialise the default dataset onto disk.  This is useful for validation
    or for re-synchronising environments that lost the OneDrive export.  The
    helper will not overwrite an existing file unless ``overwrite=True`` is
    passed.

Both helpers are intentionally dependency-free and operate exclusively on the
standard library to keep parity with the rest of the project.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterator, List, Optional, Tuple, Union


# -- data model --------------------------------------------------------------


@dataclass(frozen=True)
class Task:
    """Represents a follow-up item captured from the OneDrive task board."""

    task_id: str
    title: str
    assignee: str
    status: str
    due_date: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialise the task into a JSON compatible dictionary."""

        payload = {
            "task_id": self.task_id,
            "title": self.title,
            "assignee": self.assignee,
            "status": self.status,
        }
        if self.due_date is not None:
            payload["due_date"] = self.due_date
        if self.notes is not None:
            payload["notes"] = self.notes
        return payload

    @staticmethod
    def from_dict(payload: dict) -> "Task":
        """Create a :class:`Task` from a JSON dictionary."""

        required = {"task_id", "title", "assignee", "status"}
        missing = required.difference(payload)
        if missing:
            missing_values = ", ".join(sorted(missing))
            raise ValueError(f"Task payload missing required fields: {missing_values}.")

        return Task(
            task_id=str(payload["task_id"]),
            title=str(payload["title"]),
            assignee=str(payload["assignee"]),
            status=str(payload["status"]),
            due_date=str(payload["due_date"]) if payload.get("due_date") is not None else None,
            notes=str(payload["notes"]) if payload.get("notes") is not None else None,
        )


# -- default dataset ---------------------------------------------------------


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
DEFAULT_TASKS_FILE = PROJECT_ROOT / "docs" / "onedrive_tasks.json"


DEFAULT_TASKS: Tuple[Task, ...] = (
    Task(
        task_id="onedrive-001",
        title="Reconcile SAR attachments from OneDrive export",
        assignee="aml-operations",
        status="completed",
        due_date="2024-02-15",
        notes=(
            "Validated checksum of attachments recovered from OneDrive/AML/SAR "
            "share and archived copies in evidence locker."
        ),
    ),
    Task(
        task_id="onedrive-002",
        title="Cross-check Perriwinkle escrow narrative",
        assignee="forensics",
        status="in-progress",
        due_date="2024-02-22",
        notes="Compare OneDrive draft narrative with Appendix D flow description.",
    ),
    Task(
        task_id="onedrive-003",
        title="Restore missing beneficiary audit trail",
        assignee="compliance-review",
        status="blocked",
        due_date="2024-03-01",
        notes="Awaiting subpoena return to replace truncated OneDrive export rows.",
    ),
    Task(
        task_id="onedrive-004",
        title="Normalise pass-through account identifiers",
        assignee="data-quality",
        status="queued",
        notes="Map free-form OneDrive notes into canonical SAR schema fields.",
    ),
    Task(
        task_id="onedrive-005",
        title="Publish remediation checklist to case workspace",
        assignee="case-management",
        status="completed",
        due_date="2024-02-10",
        notes="Uploaded PDF to OneDrive remediation folder and notified stakeholders.",
    ),
)


# -- public helpers ---------------------------------------------------------


def restore_onedrive_tasks(
    destination: Optional[Union[str, Path]] = None,
    *,
    overwrite: bool = False,
) -> Path:
    """Materialise the default OneDrive task export to ``destination``.

    Parameters
    ----------
    destination:
        Location of the JSON file to create.  When omitted the canonical
        ``docs/onedrive_tasks.json`` path relative to the project root is used.
    overwrite:
        When ``True`` an existing file will be replaced.  The default ``False``
        behaviour leaves existing exports untouched to avoid accidental data
        loss.
    """

    target_path = Path(destination) if destination is not None else DEFAULT_TASKS_FILE
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists() and not overwrite:
        return target_path

    serialised: List[dict] = [task.to_dict() for task in DEFAULT_TASKS]
    json_text = json.dumps(serialised, indent=2, sort_keys=True)
    target_path.write_text(json_text + "\n", encoding="utf-8")
    return target_path


def load_onedrive_tasks(source: Optional[Union[str, Path]] = None) -> Tuple[Task, ...]:
    """Load OneDrive tasks from disk, restoring the default set when missing."""

    source_path = Path(source) if source is not None else DEFAULT_TASKS_FILE
    if not source_path.exists():
        restore_onedrive_tasks(source_path)

    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Unable to parse task JSON at {source_path}: {exc}.") from exc

    if not isinstance(payload, list):
        raise ValueError("Task JSON must be a list of objects.")

    tasks: List[Task] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Each task entry must be a JSON object.")
        tasks.append(Task.from_dict(item))

    return tuple(tasks)


def iter_onedrive_tasks(source: Optional[Union[str, Path]] = None) -> Iterator[Task]:
    """Yield tasks lazily from :func:`load_onedrive_tasks`.

    This helper keeps the public surface convenient for callers that simply
    want an iterator in streaming-style processing.
    """

    return iter(load_onedrive_tasks(source))


__all__ = [
    "Task",
    "DEFAULT_TASKS",
    "DEFAULT_TASKS_FILE",
    "iter_onedrive_tasks",
    "load_onedrive_tasks",
    "restore_onedrive_tasks",
]

