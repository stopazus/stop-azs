# stop-azs

Utilities for inspecting "Master Casebook" bundles that ship with metadata,
SHA manifests, and supporting documentation.  The library focuses on
validating bundle integrity and exposing the manifest and metadata in a
friendly Python API.

## Features

- Parse flexible SHA manifest formats (GNU, BSD, and `filename: digest`).
- Load bundle archives, compute file hashes, and surface metadata.
- Generate validation reports and lightweight bundle summaries.

## Working with bundles

1. Download the `Master_Casebook_vNext_Bundle.zip` archive and place it in a
   convenient location (for example, the shared OneDrive folder at
   `C:\Users\stopazs\OneDrive - H S HOLDING LLC\.vscode\extensions` so that it is
   available to the whole team).
2. Load the archive with `CasebookBundle` to inspect the metadata and verify
   the contents:

   ```python
   from stop_azs.bundle import CasebookBundle

   bundle = CasebookBundle.load("/path/to/Master_Casebook_vNext_Bundle.zip")
   report = bundle.validate()

   if report.is_valid:
       print("Bundle checksums match the manifest")
   else:
       print(report.mismatched_digests)
   ```

## Running the tests

```bash
pytest
```
