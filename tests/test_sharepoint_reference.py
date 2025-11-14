import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
INTEGRITY_PATH = REPO_ROOT / "docs" / "integrity_verification.md"

EXPECTED_URL = (
    "https://hsholdingllc-my.sharepoint.com/:x:/g/personal/"
    "sharon_peertel_us1/EdJxHwAcuLNNmsXyiZa44l8ByORYJsT0Fc2c8ra3sAGeag?e=nyhiho"
)

ARTIFACT_NAME = "Electronic_Dispatch_Packet_2025-10-11_vFinal.zip"
RETRIEVAL_NOTE = "October 12, 2025 at 14:22 UTC"
ACCESS_NOTE = "Access control: Restricted to N & S Holding LLC"


def test_readme_contains_sharepoint_link():
    readme_text = README_PATH.read_text(encoding="utf-8")
    assert EXPECTED_URL in readme_text, "README is missing the SharePoint reference"


def test_integrity_sheet_contains_sharepoint_link():
    integrity_text = INTEGRITY_PATH.read_text(encoding="utf-8")
    assert EXPECTED_URL in integrity_text, "Integrity sheet is missing the SharePoint reference"


def test_readme_records_sharepoint_artifact_details():
    readme_text = README_PATH.read_text(encoding="utf-8")
    assert ARTIFACT_NAME in readme_text, "README must document the hosted SharePoint artifact name"
    assert RETRIEVAL_NOTE in readme_text, "README must record the SharePoint retrieval timestamp"
    assert ACCESS_NOTE in readme_text, "README must describe SharePoint access controls"


def test_integrity_sheet_records_sharepoint_artifact_details():
    integrity_text = INTEGRITY_PATH.read_text(encoding="utf-8")
    assert ARTIFACT_NAME in integrity_text, "Integrity sheet must document the hosted SharePoint artifact name"
    assert RETRIEVAL_NOTE in integrity_text, "Integrity sheet must record the SharePoint retrieval timestamp"
    assert ACCESS_NOTE in integrity_text, "Integrity sheet must describe SharePoint access controls"
