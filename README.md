# Project Overview

This README provides information about the project and instructions for contributors.

## Project Details

| Field | Value |
|---|---|
| Project ID | READMETX10002 |
| Date/Time (UTC) | 2025-01-12T17:41:39Z |
| Date (Local) | 1/12/2025 |
| Transaction Type | WIRE |
| Amount | 248500 |
| Direction | OUT |
| Originator/Beneficiary | YBH 2948 LLC |
| Originator Bank | OptimumBank |
| Originator SWIFT/BIC | OPTMUS3X |
| Beneficiary | Zeig Law PLLC IOTA |
| Beneficiary Bank | City National Bank (CNB) |
| Beneficiary SWIFT/BIC | CNBUS33 |
| File Reference 1 | FILE-24-981 |
| File Reference 2 | FILE-24-981-D1 |
| Description | Disbursement per instruction – File 24-981 |
| Flag 1 | TRUE |
| Flag 2 | TRUE |
| Flag 3 | TRUE |
| Flag 4 | TRUE |
| Status | passed |
| Verification | originator/beneficiary on file |
| Category | Treasury/Wires |
| Review Date | 2025-10-20T00:00:00Z |

## Contributing

Thanks for helping out! Do these one-time steps to get a clean local setup.

### 1) Prerequisites
- `jq` (required) — macOS: `brew install jq` · Ubuntu: `sudo apt-get install jq`
- `zsh` (recommended)
- `watch` (optional) — macOS: `brew install watch`
- `shellcheck` (for lint) — macOS: `brew install shellcheck` · Ubuntu: `sudo apt-get install shellcheck`

### 2) Install shell helpers
```sh
# zsh (default)
make install-shell-helpers
source ~/.zshrc

# bash (if you use ~/.bashrc)
SHELL_RC="$HOME/.bashrc" make install-shell-helpers
source "$HOME/.bashrc"
```

Verify:
```sh
drs --help
drw --help
make post-install-check
```

### 3) Git hooks (pre-commit)
Install our pre-commit hook (runs `make lint-sh` and blocks commits on errors):
```sh
make install-githooks
```
Remove later with:
```sh
make uninstall-githooks
```

### 4) Quick local checks
```sh
# Lint shell scripts
make lint-sh

# Smoke tests (fast)
INTERVAL=1 DURATION=15s make drw-idle
INTERVAL=1 DURATION=15s make drw-work
```

### Handy make targets
- `install-shell-helpers` — add `drs`/`drw` to your shell rc (idempotent)
- `post-install-check` — doctor: verifies jq/paths/helpers
- `drw-idle` / `drw-work` — quick condition smoke tests
- `lint-sh` — ShellCheck on `scripts/*.sh`
- `install-githooks` / `uninstall-githooks` — manage pre-commit hook

### CI (what runs on PRs)
- **Smoketests:** `drw-idle` and `drw-work` (matrix: Ubuntu + macOS); PRs also have a quick 10s run.
- **ShellCheck:** lints `scripts/*.sh`.
- **Concurrency:** new pushes cancel older runs for the same PR/branch.

### Bootstrap (one command)

Runs `install-shell-helpers` → `post-install-check` → `install-githooks`.

```sh
# zsh (default)
make bootstrap
source ~/.zshrc

# bash users
SHELL_RC="$HOME/.bashrc" make bootstrap
source "$HOME/.bashrc"

# verify
drs --help && drw --help
```
