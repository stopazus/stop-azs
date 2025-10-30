from __future__ import annotations

import hashlib
import io
import json
import zipfile

import pytest

from stop_azs.bundle import CasebookBundle, parse_sha_manifest

_METADATA = {
    "title": "Master Casebook vNext",
    "version": "2024.09",
    "entries": 42,
}

_PDF_BYTES = b"%PDF-sample%\n"
_README_BYTES = b"This is a test bundle.\n"
_METADATA_BYTES = json.dumps(_METADATA, indent=2).encode("utf-8")

_DIGESTS = {
    "Master_Casebook_Bundle_vNext.pdf": hashlib.sha256(_PDF_BYTES).hexdigest(),
    "README.txt": hashlib.sha256(_README_BYTES).hexdigest(),
    "Binder_Metadata.json": hashlib.sha256(_METADATA_BYTES).hexdigest(),
}


def _build_bundle_with_manifest(manifest_lines: list[str]) -> bytes:
    if not manifest_lines:
        manifest_lines = [
            f"{hash_value}  {filename}"
            for filename, hash_value in _DIGESTS.items()
        ]

    manifest_bytes = "\n".join(manifest_lines).encode("utf-8")

    file_obj = io.BytesIO()
    with zipfile.ZipFile(file_obj, "w") as archive:
        archive.writestr("Master_Casebook_Bundle_vNext.pdf", _PDF_BYTES)
        archive.writestr("README.txt", _README_BYTES)
        archive.writestr("Binder_Metadata.json", _METADATA_BYTES)
        archive.writestr("SHA-Manifest.txt", manifest_bytes)

    return file_obj.getvalue()


@pytest.fixture()
def sample_bundle_bytes() -> bytes:
    return _build_bundle_with_manifest([])


def test_parse_sha_manifest_accepts_multiple_formats():
    sha_lines = "\n".join(
        [
            "a" * 64 + "  README.txt",
            "SHA256 (Binder_Metadata.json) = " + "b" * 64,
            "Master_Casebook_Bundle_vNext.pdf: " + "c" * 64,
        ]
    )

    mapping = parse_sha_manifest(sha_lines)

    assert mapping["README.txt"] == "a" * 64
    assert mapping["Binder_Metadata.json"] == "b" * 64
    assert mapping["Master_Casebook_Bundle_vNext.pdf"] == "c" * 64


def test_parse_sha_manifest_ignores_bom_and_comments():
    digest = "a" * 64
    text = "\ufeff# header\n" + f"{digest}  README.txt"

    mapping = parse_sha_manifest(text)

    assert mapping == {"README.txt": digest}


def test_parse_sha_manifest_normalises_prefixed_names():
    digest = "b" * 64
    mapping = parse_sha_manifest(f"*README.txt: {digest}")

    assert mapping == {"README.txt": digest}


def test_parse_sha_manifest_rejects_duplicate_entries():
    digest = "c" * 64
    with pytest.raises(ValueError):
        parse_sha_manifest(f"README.txt: {digest}\nREADME.txt: {'d' * 64}")


def test_casebook_bundle_loads_and_validates(sample_bundle_bytes: bytes):
    bundle = CasebookBundle.load(sample_bundle_bytes)

    report = bundle.validate()

    assert report.is_valid
    assert report.missing_from_manifest == ()

    summary = bundle.summary()
    assert summary["file_count"] == 4
    assert summary["manifest_entries"] == 3
    assert summary["metadata"]["title"] == "Master Casebook vNext"

    pdf_member = bundle.get_member("Master_Casebook_Bundle_vNext.pdf")
    assert pdf_member.sha256 == bundle.manifest[pdf_member.name]


def test_casebook_bundle_detects_modified_file(sample_bundle_bytes: bytes):
    bundle = CasebookBundle.load(sample_bundle_bytes)

    tampered = dict(bundle.members)
    tampered["README.txt"] = tampered["README.txt"].__class__(
        name="README.txt",
        size=tampered["README.txt"].size,
        sha256="0" * 64,
        data=b"tampered",
    )
    bundle_with_tamper = CasebookBundle(tampered, bundle.manifest)

    report = bundle_with_tamper.validate()

    assert not report.is_valid
    assert "README.txt" in report.mismatched_digests


def test_casebook_bundle_load_handles_manifest_with_bom():
    manifest_lines = [
        f"\ufeff{_DIGESTS['README.txt']}  README.txt",
        f"{_DIGESTS['Master_Casebook_Bundle_vNext.pdf']}  Master_Casebook_Bundle_vNext.pdf",
        f"{_DIGESTS['Binder_Metadata.json']}  Binder_Metadata.json",
    ]

    bundle = CasebookBundle.load(_build_bundle_with_manifest(manifest_lines))

    report = bundle.validate()

    assert report.is_valid
