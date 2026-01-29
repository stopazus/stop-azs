import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the module under test
sys.path.insert(0, str(ROOT / "tools"))
from aml_exhibit_builder import parse_args, build_packet, render_markdown, render_json


class TestApprovalModeArgument(unittest.TestCase):
    """Test the --approval-mode command-line argument."""

    def test_default_approval_mode_is_manual(self) -> None:
        """Test that the default approval mode is 'manual' when not specified."""
        test_args = [
            "aml_exhibit_builder.py",
            "--packet-id", "PKT-001",
            "--imsi-prefix", "310260",
            "--sim-country-iso", "US",
            "--network-operator", "310260",
            "--network-operator-name", "T-Mobile USA",
            "--network-type", "LTE",
            "--msisdn", "+1234567890",
            "--capture-source", "Test Source",
            "--scheme", "Test Scheme",
        ]
        with patch("sys.argv", test_args):
            args = parse_args()
            self.assertEqual(args.approval_mode, "manual")

    def test_approval_mode_full_auto(self) -> None:
        """Test that --approval-mode full-auto is accepted and stored."""
        test_args = [
            "aml_exhibit_builder.py",
            "--packet-id", "PKT-002",
            "--imsi-prefix", "310260",
            "--sim-country-iso", "US",
            "--network-operator", "310260",
            "--network-operator-name", "T-Mobile USA",
            "--network-type", "LTE",
            "--msisdn", "+1234567890",
            "--capture-source", "Test Source",
            "--scheme", "Test Scheme",
            "--approval-mode", "full-auto",
        ]
        with patch("sys.argv", test_args):
            args = parse_args()
            self.assertEqual(args.approval_mode, "full-auto")

    def test_approval_mode_manual(self) -> None:
        """Test that --approval-mode manual is accepted and stored."""
        test_args = [
            "aml_exhibit_builder.py",
            "--packet-id", "PKT-003",
            "--imsi-prefix", "310260",
            "--sim-country-iso", "US",
            "--network-operator", "310260",
            "--network-operator-name", "T-Mobile USA",
            "--network-type", "LTE",
            "--msisdn", "+1234567890",
            "--capture-source", "Test Source",
            "--scheme", "Test Scheme",
            "--approval-mode", "manual",
        ]
        with patch("sys.argv", test_args):
            args = parse_args()
            self.assertEqual(args.approval_mode, "manual")


class TestApprovalModeInPacket(unittest.TestCase):
    """Test that approval mode is properly stored in the ExhibitPacket."""

    def test_packet_contains_approval_mode(self) -> None:
        """Test that build_packet includes approval_mode in the packet."""
        test_args = [
            "aml_exhibit_builder.py",
            "--packet-id", "PKT-004",
            "--imsi-prefix", "310260",
            "--sim-country-iso", "US",
            "--network-operator", "310260",
            "--network-operator-name", "T-Mobile USA",
            "--network-type", "LTE",
            "--msisdn", "+1234567890",
            "--capture-source", "Test Source",
            "--scheme", "Test Scheme",
            "--approval-mode", "full-auto",
        ]
        with patch("sys.argv", test_args):
            args = parse_args()
            packet = build_packet(args)
            self.assertEqual(packet.approval_mode, "full-auto")


class TestApprovalModeInMarkdownOutput(unittest.TestCase):
    """Test that approval mode appears in Markdown output."""

    def test_markdown_includes_approval_mode(self) -> None:
        """Test that render_markdown includes the approval mode."""
        test_args = [
            "aml_exhibit_builder.py",
            "--packet-id", "PKT-005",
            "--imsi-prefix", "310260",
            "--sim-country-iso", "US",
            "--network-operator", "310260",
            "--network-operator-name", "T-Mobile USA",
            "--network-type", "LTE",
            "--msisdn", "+1234567890",
            "--capture-source", "Test Source",
            "--scheme", "Test Scheme",
            "--approval-mode", "full-auto",
        ]
        with patch("sys.argv", test_args):
            args = parse_args()
            packet = build_packet(args)
            markdown = render_markdown(packet)
            self.assertIn("**Approval Mode:** full-auto", markdown)

    def test_markdown_default_manual_mode(self) -> None:
        """Test that render_markdown shows 'manual' when approval mode is default."""
        test_args = [
            "aml_exhibit_builder.py",
            "--packet-id", "PKT-006",
            "--imsi-prefix", "310260",
            "--sim-country-iso", "US",
            "--network-operator", "310260",
            "--network-operator-name", "T-Mobile USA",
            "--network-type", "LTE",
            "--msisdn", "+1234567890",
            "--capture-source", "Test Source",
            "--scheme", "Test Scheme",
        ]
        with patch("sys.argv", test_args):
            args = parse_args()
            packet = build_packet(args)
            markdown = render_markdown(packet)
            self.assertIn("**Approval Mode:** manual", markdown)


class TestApprovalModeInJsonOutput(unittest.TestCase):
    """Test that approval mode appears in JSON output."""

    def test_json_includes_approval_mode(self) -> None:
        """Test that render_json includes the approval mode."""
        test_args = [
            "aml_exhibit_builder.py",
            "--packet-id", "PKT-007",
            "--imsi-prefix", "310260",
            "--sim-country-iso", "US",
            "--network-operator", "310260",
            "--network-operator-name", "T-Mobile USA",
            "--network-type", "LTE",
            "--msisdn", "+1234567890",
            "--capture-source", "Test Source",
            "--scheme", "Test Scheme",
            "--approval-mode", "full-auto",
        ]
        with patch("sys.argv", test_args):
            args = parse_args()
            packet = build_packet(args)
            json_output = render_json(packet)
            data = json.loads(json_output)
            self.assertEqual(data["approval_mode"], "full-auto")


if __name__ == "__main__":
    unittest.main()
