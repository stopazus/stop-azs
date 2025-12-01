# SAR Parser Utilities

This repository contains helper utilities for working with Suspicious Activity Report (SAR)
documents.  The library provides validation helpers via ``sar_parser.validator`` and a
small toolkit for managing the default task dataset that ships with the project.

## Quick start

Most callers can import directly from :mod:`sar_parser` instead of reaching into the
individual submodules.  The package re-exports the common validator helpers and OneDrive
task utilities, so a minimal usage example looks like:

```python
from sar_parser import validate_document, load_onedrive_tasks

document = {...}  # SAR payload
tasks = load_onedrive_tasks()
validate_document(document)
```

The :func:`validate_document` helper raises :class:`sar_parser.ValidationError` with a
rich error payload when the report fails structural or semantic checks.  Loading tasks
through the top-level API ensures the dataset is restored automatically before
consumption, mirroring the behaviour exercised in the unit test suite.

## Task dataset helpers

The :mod:`sar_parser.tasks` module exposes a lightweight API to recover the default
OneDrive task export that accompanies the documentation.  When the shared storage copy
is missing, ``restore_onedrive_tasks`` can rebuild the canonical JSON file on disk.
Callers can then load the data either eagerly with ``load_onedrive_tasks`` or lazily via
``iter_onedrive_tasks`` which yields :class:`sar_parser.tasks.Task` instances.

The packaged dataset lives at ``docs/onedrive_tasks.json`` after restoration and mirrors
the structure expected by downstream integration tests.

### Example

```python
from sar_parser.tasks import load_onedrive_tasks

for task in load_onedrive_tasks():
    print(task.title, "=>", task.status)
```

The helper automatically recreates the ``docs/onedrive_tasks.json`` file when it has been
deleted, so the snippet above always succeeds without any additional setup steps.
