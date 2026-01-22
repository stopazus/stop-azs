#!/usr/bin/env bash
set -euo pipefail

echo "Starting full release check..."

if command -v python >/dev/null 2>&1; then
  echo "Python version: $(python --version 2>&1)"
fi

echo "Running pytest to validate SAR parser..."
pytest

echo "Release checks completed successfully."
