#!/usr/bin/env python3
"""External resource update tracker.

This script manages the status and update tracking for external research
resources listed in docs/external_resources.md. It provides functionality to:

* Check the last update time for external resources
* Track sync status with external workspaces
* Generate live status indicators for resource availability
* Update the external resources table with current status

The tool is designed to work with the investigative team's workflow where
external AI-assisted drafts and research are synchronized into the repository.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class ExternalResource:
    """Represents an external research resource."""

    name: str
    url: str
    custodian: str
    notes: str
    last_updated: Optional[str] = None
    status: str = "unknown"


@dataclass
class ResourceStatus:
    """Container for resource status information."""

    resources: List[ExternalResource]
    checked_at: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track and update status of external research resources.",
    )
    parser.add_argument(
        "--resources-file",
        default="docs/external_resources.md",
        help="Path to the external resources markdown file (default: docs/external_resources.md).",
    )
    parser.add_argument(
        "--output-format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format for status report (default: markdown).",
    )
    parser.add_argument(
        "--status-file",
        help="Optional path to save status tracking data as JSON.",
    )
    parser.add_argument(
        "--update-resource",
        help="Mark a specific resource as recently updated (provide resource name).",
    )
    parser.add_argument(
        "--check-live",
        action="store_true",
        help="Check live status of resources (placeholder for future connectivity checks).",
    )
    return parser.parse_args()


def parse_resources_table(content: str) -> List[ExternalResource]:
    """Extract resource entries from the markdown table."""

    resources = []
    # Find the table in the markdown
    lines = content.split("\n")
    in_table = False
    header_passed = False

    for line in lines:
        line = line.strip()
        if line.startswith("| Resource |"):
            in_table = True
            continue
        if in_table and line.startswith("| ---"):
            header_passed = True
            continue
        if in_table and header_passed and line.startswith("|"):
            # Parse table row
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:  # Account for leading/trailing pipes
                name = parts[1]
                url = parts[2]
                custodian = parts[3]
                notes = parts[4]
                if name and url and name != "Resource":
                    resources.append(
                        ExternalResource(
                            name=name,
                            url=url,
                            custodian=custodian,
                            notes=notes,
                        )
                    )
        elif in_table and not line.startswith("|"):
            # End of table
            break

    return resources


def load_status_file(status_path: str) -> dict:
    """Load existing status tracking data."""

    path = Path(status_path)
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_status_file(status_path: str, status: ResourceStatus) -> None:
    """Save status tracking data to JSON file."""

    path = Path(status_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to simplified format for storage
    data = {
        "checked_at": status.checked_at,
        "resources": {
            r.name: {
                "last_updated": r.last_updated,
                "status": r.status,
            }
            for r in status.resources
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_resource_status(
    resources: List[ExternalResource],
    resource_name: str,
    status_data: dict,
) -> None:
    """Mark a resource as recently updated."""

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for resource in resources:
        if resource.name == resource_name:
            resource.last_updated = now
            resource.status = "live"
            # Update status tracking
            if "resources" not in status_data:
                status_data["resources"] = {}
            status_data["resources"][resource_name] = {
                "last_updated": now,
                "status": "live",
            }
            break


def apply_status_data(resources: List[ExternalResource], status_data: dict) -> None:
    """Apply saved status data to resources."""

    resource_status = status_data.get("resources", {})
    for resource in resources:
        if resource.name in resource_status:
            saved = resource_status[resource.name]
            resource.last_updated = saved.get("last_updated")
            resource.status = saved.get("status", "unknown")


def check_live_status(resources: List[ExternalResource]) -> None:
    """Check live availability of resources (placeholder for future implementation)."""

    # This is a placeholder for future functionality that could:
    # - Check if URLs are accessible
    # - Verify API connectivity
    # - Update status based on actual checks
    for resource in resources:
        if resource.status == "unknown":
            resource.status = "not_checked"


def render_markdown_status(status: ResourceStatus) -> str:
    """Generate a markdown status report."""

    lines = ["# External Resources Status", ""]
    lines.append(f"**Checked At:** {status.checked_at}")
    lines.append("")
    lines.append("| Resource | Status | Last Updated | URL |")
    lines.append("| --- | --- | --- | --- |")

    for resource in status.resources:
        status_indicator = {
            "live": "🟢 Live",
            "stale": "🟡 Stale",
            "unknown": "⚪ Unknown",
            "not_checked": "⚪ Not Checked",
            "error": "🔴 Error",
        }.get(resource.status, "⚪ Unknown")

        last_updated = resource.last_updated or "Never"
        lines.append(
            f"| {resource.name} | {status_indicator} | {last_updated} | {resource.url} |"
        )

    return "\n".join(lines)


def render_json_status(status: ResourceStatus) -> str:
    """Generate a JSON status report."""

    data = asdict(status)
    return json.dumps(data, indent=2, ensure_ascii=False)


def main() -> None:
    args = parse_args()

    # Load the resources markdown file
    resources_path = Path(args.resources_file)
    if not resources_path.exists():
        print(f"Error: Resources file not found: {args.resources_file}")
        return

    content = resources_path.read_text(encoding="utf-8")
    resources = parse_resources_table(content)

    if not resources:
        print("Warning: No resources found in the markdown table")
        return

    # Load existing status data if available
    status_data = {}
    if args.status_file:
        status_data = load_status_file(args.status_file)

    # Apply existing status
    apply_status_data(resources, status_data)

    # Update specific resource if requested
    if args.update_resource:
        update_resource_status(resources, args.update_resource, status_data)

    # Check live status if requested
    if args.check_live:
        check_live_status(resources)

    # Create status object
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status = ResourceStatus(resources=resources, checked_at=checked_at)

    # Save status file if path provided
    if args.status_file:
        save_status_file(args.status_file, status)

    # Generate and print report
    if args.output_format == "markdown":
        report = render_markdown_status(status)
    else:
        report = render_json_status(status)

    print(report)


if __name__ == "__main__":
    main()
