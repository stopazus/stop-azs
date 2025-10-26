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
provided metadata, the agency's leadership contact, and a five-character base
code that can be used when coordinating across systems. Attach supporting
documentation, timelines, and communications that the agency will need to take
action on the case.

The path helpers also accept POSIX-style paths and relative folders, ensuring
that packages are created in the expected location regardless of the calling
platform. You can customise agencies by instantiating :class:`stop_azs.AgencyContact`
with the ``director`` attribute populated; the ``base_code()`` helper returns a
five-character mnemonic derived from the agency and program names.
