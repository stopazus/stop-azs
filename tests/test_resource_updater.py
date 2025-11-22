import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import from tools directory
sys.path.insert(0, str(ROOT / "tools"))
from resource_updater import (
    ExternalResource,
    ResourceStatus,
    parse_resources_table,
    apply_status_data,
    render_markdown_status,
    render_json_status,
)


SAMPLE_MARKDOWN = """\
# External Research Resources

The investigative team often supplements the forensic ledger review with
open-source intelligence tools.

| Resource | URL | Custodian | Notes |
| --- | --- | --- | --- |
| Gemini Workbench | https://gemini.google.com/app/8f7e04aa81aa552a | Case Lead | AI-assisted write-ups |
| Test Resource | https://example.com/test | Test Custodian | Test notes |

## Operational Guidance

More text here.
"""


class ParseResourcesTableTests(unittest.TestCase):
    def test_parses_table_correctly(self) -> None:
        resources = parse_resources_table(SAMPLE_MARKDOWN)
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0].name, "Gemini Workbench")
        self.assertEqual(resources[0].url, "https://gemini.google.com/app/8f7e04aa81aa552a")
        self.assertEqual(resources[0].custodian, "Case Lead")
        self.assertEqual(resources[0].notes, "AI-assisted write-ups")
        self.assertEqual(resources[1].name, "Test Resource")

    def test_handles_empty_table(self) -> None:
        markdown = "# Header\n\nNo table here."
        resources = parse_resources_table(markdown)
        self.assertEqual(len(resources), 0)


class ApplyStatusDataTests(unittest.TestCase):
    def test_applies_status_to_matching_resources(self) -> None:
        resources = [
            ExternalResource(
                name="Test Resource",
                url="https://example.com",
                custodian="Test",
                notes="Notes",
            )
        ]
        status_data = {
            "resources": {
                "Test Resource": {
                    "last_updated": "2025-11-22T10:00:00+00:00",
                    "status": "live",
                }
            }
        }

        apply_status_data(resources, status_data)

        self.assertEqual(resources[0].status, "live")
        self.assertEqual(resources[0].last_updated, "2025-11-22T10:00:00+00:00")

    def test_ignores_non_matching_resources(self) -> None:
        resources = [
            ExternalResource(
                name="Test Resource",
                url="https://example.com",
                custodian="Test",
                notes="Notes",
            )
        ]
        status_data = {
            "resources": {
                "Different Resource": {
                    "last_updated": "2025-11-22T10:00:00+00:00",
                    "status": "live",
                }
            }
        }

        apply_status_data(resources, status_data)

        self.assertEqual(resources[0].status, "unknown")
        self.assertIsNone(resources[0].last_updated)


class RenderMarkdownStatusTests(unittest.TestCase):
    def test_renders_markdown_with_status_indicators(self) -> None:
        resources = [
            ExternalResource(
                name="Live Resource",
                url="https://example.com/live",
                custodian="Test",
                notes="Notes",
                last_updated="2025-11-22T10:00:00+00:00",
                status="live",
            ),
            ExternalResource(
                name="Unknown Resource",
                url="https://example.com/unknown",
                custodian="Test",
                notes="Notes",
            ),
        ]
        status = ResourceStatus(
            resources=resources, checked_at="2025-11-22T12:00:00+00:00"
        )

        markdown = render_markdown_status(status)

        self.assertIn("# External Resources Status", markdown)
        self.assertIn("**Checked At:** 2025-11-22T12:00:00+00:00", markdown)
        self.assertIn("🟢 Live", markdown)
        self.assertIn("⚪ Unknown", markdown)
        self.assertIn("Live Resource", markdown)
        self.assertIn("Unknown Resource", markdown)


class RenderJsonStatusTests(unittest.TestCase):
    def test_renders_valid_json(self) -> None:
        import json

        resources = [
            ExternalResource(
                name="Test",
                url="https://example.com",
                custodian="Test",
                notes="Notes",
                status="live",
            )
        ]
        status = ResourceStatus(
            resources=resources, checked_at="2025-11-22T12:00:00+00:00"
        )

        json_output = render_json_status(status)
        data = json.loads(json_output)  # Should not raise

        self.assertEqual(data["checked_at"], "2025-11-22T12:00:00+00:00")
        self.assertEqual(len(data["resources"]), 1)
        self.assertEqual(data["resources"][0]["name"], "Test")


if __name__ == "__main__":
    unittest.main()
