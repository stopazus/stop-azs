import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
INTEGRITY_PATH = REPO_ROOT / "docs" / "integrity_verification.md"

EXPECTED_URL = (
    "https://hsholdingllc-my.sharepoint.com/:x:/g/personal/"
    "sharon_peertel_us1/EdJxHwAcuLNNmsXyiZa44l8ByORYJsT0Fc2c8ra3sAGeag?e=nyhiho"
)


def test_readme_contains_sharepoint_link():
    readme_text = README_PATH.read_text(encoding="utf-8")
    assert EXPECTED_URL in readme_text, "README is missing the SharePoint reference"


def test_integrity_sheet_contains_sharepoint_link():
    integrity_text = INTEGRITY_PATH.read_text(encoding="utf-8")
    assert EXPECTED_URL in integrity_text, "Integrity sheet is missing the SharePoint reference"
