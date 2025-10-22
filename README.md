# stop-azs

Utilities for assembling regulatory submission packages that coordinate across
multiple agencies. The library provides helpers to normalize Windows-style
paths and generate a directory structure containing per-agency documentation.

## Quick start

```python
from stop_azs import create_submission_package, DEFAULT_AGENCIES

package_root = create_submission_package(
    base_path=r"C:\\Users\\stopazs\\OneDrive - H S HOLDING LLC\\N_S_Holding_Master_Submission_Packag",
    case_id="Case-2025-10-15",
    metadata={"Subject": "Account takeover investigation"},
)

print(package_root)
```
```
/workspace/.../OneDrive - H S HOLDING LLC/N_S_Holding_Master_Submission_Packag/Case-2025-10-15
```

Each agency receives a dedicated folder containing a Markdown brief with the
provided metadata and a reminder to attach supporting documentation.

The path helpers also accept POSIX-style paths and relative folders, ensuring
that packages are created in the expected location regardless of the calling
platform.
