from __future__ import annotations

from pathlib import Path

import pytest

from stop_azs import AgencyContact, DEFAULT_AGENCIES, create_submission_package, normalize_submission_path


@pytest.mark.parametrize(
    "raw_path,expected_parts",
    [
        (
            r"C:\\Users\\stopazs\\OneDrive - H S HOLDING LLC\\N_S_Holding_Master_Submission_Packag",
            [
                "Users",
                "stopazs",
                "OneDrive - H S HOLDING LLC",
                "N_S_Holding_Master_Submission_Packag",
            ],
        ),
        (
            r"\\\OneDrive\\CaseFiles",
            ["OneDrive", "CaseFiles"],
        ),
    ],
)
def test_normalize_submission_path(raw_path: str, expected_parts: list[str], tmp_path: Path) -> None:
    normalized = normalize_submission_path(raw_path, base_dir=tmp_path)
    assert normalized.parts[-len(expected_parts) :] == tuple(expected_parts)


def test_normalize_submission_path_accepts_posix_absolute(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "packages"
    normalized = normalize_submission_path(target)
    assert normalized == target


def test_normalize_submission_path_accepts_posix_relative(tmp_path: Path) -> None:
    normalized = normalize_submission_path("packages", base_dir=tmp_path)
    assert normalized == tmp_path / "packages"


def test_agency_contact_handles_director_and_base_code() -> None:
    contact = AgencyContact(
        agency="Ægency", program="123", director="Director Name", reference="Ref"
    )

    block = contact.formatted_block()
    assert "**Director:** Director Name" in block
    assert "**Base Code:**" in block
    code = contact.base_code()
    assert len(code) == 5
    assert code.isupper()


def test_default_agencies_include_directors() -> None:
    for agency in DEFAULT_AGENCIES:
        assert agency.director is not None


@pytest.mark.parametrize(
    "raw_path",
    [
        r"C:\\Users\\..\\..\\bad",
        r"..\\escape",
        "../../outside",
    ],
)
def test_normalize_submission_path_rejects_traversal(raw_path: str) -> None:
    with pytest.raises(ValueError):
        normalize_submission_path(raw_path)


def test_create_submission_package_builds_structure(tmp_path: Path) -> None:
    base = tmp_path / "packages"
    case_id = "Case-0001"
    metadata = {"Subject": "Wire fraud", "Amount": "$120,000"}

    package_path = create_submission_package(base, case_id, metadata=metadata)

    assert package_path.exists()
    summary = package_path / "SUMMARY.md"
    assert summary.exists()
    summary_text = summary.read_text(encoding="utf-8")
    for key, value in metadata.items():
        assert f"**{key}:** {value}" in summary_text
    for agency in DEFAULT_AGENCIES:
        expected_line = f"- {agency.agency} — {agency.program}"
        assert expected_line in summary_text
        if agency.director:
            assert agency.director in summary_text
        assert agency.base_code() in summary_text

    for agency in DEFAULT_AGENCIES:
        agency_dir = package_path / agency.slug()
        assert agency_dir.exists(), f"Agency directory missing for {agency.agency}"
        readme = agency_dir / "README.md"
        contents = readme.read_text(encoding="utf-8")
        assert agency.agency in contents
        if agency.reference:
            assert agency.reference in contents
        if agency.director:
            assert f"**Director:** {agency.director}" in contents
        assert f"**Base Code:** {agency.base_code()}" in contents
        for key, value in metadata.items():
            assert f"**{key}:** {value}" in contents


def test_create_submission_package_supports_custom_agencies(tmp_path: Path) -> None:
    custom_agencies = [
        AgencyContact(agency="Local Police", program="Financial Crimes Unit", reference="LP-42"),
    ]
    package_path = create_submission_package(tmp_path, "Case-002", agencies=custom_agencies)

    default_dir = package_path / DEFAULT_AGENCIES[0].slug()
    assert not default_dir.exists()

    custom_dir = package_path / custom_agencies[0].slug()
    assert custom_dir.exists()
