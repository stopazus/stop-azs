# stop-azs

Utilities for scanning task files stored in an iCloud Drive folder structure. The
library can search for JSON task definitions, apply default values to missing
fields, and filter results using a query string.

## Usage

```python
from stop_azs import scan_icloud_tasks, search_tasks

tasks = scan_icloud_tasks("/path/to/icloud/drive", defaults={"status": "todo"})
matching = search_tasks(tasks, "fbi")
```

## Running tests

```bash
pip install -e .[test]
pytest
```
