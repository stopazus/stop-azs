"""Top-level exports for SAR validation helpers and OneDrive task tooling.

The package bundles two main feature areas:

* :mod:`sar_parser.validator` for validating Suspicious Activity Reports (SAR)
  against a curated set of structural and semantic checks.
* :mod:`sar_parser.tasks` for reconstructing and loading the default OneDrive
  task export referenced throughout the project documentation.

Importing from :mod:`sar_parser` re-exports the most frequently used entry
points from both modules so callers can access them without digging into the
package structure.

Quick start example
===================

.. code-block:: python

   from sar_parser import validate_document, load_onedrive_tasks

   document = {...}  # SAR payload
   validate_document(document)
   tasks = load_onedrive_tasks()

The import side effects ensure that :func:`load_onedrive_tasks` will recreate
the bundled dataset on demand, giving callers a resilient entry point that
matches the behaviour exercised in the unit test suite.  You can also restore
the JSON export to custom locations—including paths with spaces or hyphens
such as ``/Volumes/SSD-PRO/appdata`` or ``/Volumes/SSD V7 2TB/workspace/data``—
by passing the destination into :func:`restore_onedrive_tasks`.
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
