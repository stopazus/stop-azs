"""Top-level exports for SAR validation helpers and OneDrive task tooling.

The package bundles two main feature areas:

* :mod:`sar_parser.validator` for validating Suspicious Activity Reports (SAR)
  against a curated set of structural and semantic checks.
* :mod:`sar_parser.tasks` for reconstructing and loading the default OneDrive
  task export referenced throughout the project documentation.

Importing from :mod:`sar_parser` re-exports the most frequently used entry
points from both modules so callers can access them without digging into the
package structure.
"""

from .validator import (
    ValidationError,
    ValidationResult,
    validate_document,
    validate_string,
    validate_file,
)
from .tasks import (
    Task,
    DEFAULT_TASKS,
    DEFAULT_TASKS_FILE,
    iter_onedrive_tasks,
    load_onedrive_tasks,
    restore_onedrive_tasks,
)

__all__ = [
    "ValidationError",
    "ValidationResult",
    "validate_document",
    "validate_string",
    "validate_file",
    "Task",
    "DEFAULT_TASKS",
    "DEFAULT_TASKS_FILE",
    "iter_onedrive_tasks",
    "load_onedrive_tasks",
    "restore_onedrive_tasks",
]
