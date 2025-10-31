from __future__ import annotations

from collections import OrderedDict
import importlib
import importlib.util
import sys

from urllib.error import HTTPError

import pytest


@pytest.fixture
def atlas_module():
    return importlib.import_module("stop_azs.atlas")


class DummyResponse:
    def __init__(self, status: int | None = 200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def getcode(self):
        return self.status


class DummyDownloadResponse(DummyResponse):
    def __init__(self, data: bytes, status: int | None = 200):
        super().__init__(status=status)
        self._data = data

    def read(self) -> bytes:
        return self._data


def test_package_exports_public_api(atlas_module):
    from stop_azs import (
        AtlasDataError,
        Technique,
        check_atlas_connection,
        group_techniques_by_tactic,
        load_atlas_data,
        select_matrix,
        summarise_matrix,
    )

    assert AtlasDataError is atlas_module.AtlasDataError
    assert Technique is atlas_module.Technique
    assert check_atlas_connection is atlas_module.check_atlas_connection
    assert group_techniques_by_tactic is atlas_module.group_techniques_by_tactic
    assert load_atlas_data is atlas_module.load_atlas_data
    assert select_matrix is atlas_module.select_matrix
    assert summarise_matrix is atlas_module.summarise_matrix


@pytest.fixture
def sample_data() -> dict:
    return {
        "matrices": [
            {
                "id": "ATLAS",
                "tactics": [
                    {"id": "TAC1", "name": "First"},
                    {"id": "TAC2", "name": "Second"},
                ],
                "techniques": [
                    {
                        "id": "TECH1",
                        "name": "Alpha",
                        "description": "Top level",
                        "tactics": ["TAC1"],
                    },
                    {
                        "id": "TECH1.A",
                        "name": "Variant",
                        "description": "Sub",
                        "subtechnique-of": "TECH1",
                    },
                    {
                        "id": "TECH2",
                        "name": "Bravo",
                        "description": "Second",
                        "tactics": ["TAC1", "TAC2"],
                    },
                ],
            }
        ]
    }


def test_select_matrix_returns_expected_section(atlas_module, sample_data):
    matrix = atlas_module.select_matrix(sample_data)
    assert matrix["id"] == "ATLAS"


def test_grouping_includes_parent_tactic(atlas_module, sample_data):
    matrix = atlas_module.select_matrix(sample_data)
    grouped = atlas_module.group_techniques_by_tactic(matrix)
    assert list(grouped.keys()) == ["First", "Second"]

    first_tactic = grouped["First"]
    assert [tech.id for tech in first_tactic] == ["TECH1", "TECH1.A", "TECH2"]
    variant = first_tactic[1]
    assert variant.is_subtechnique is True
    assert variant.parent_id == "TECH1"
    assert variant.display_name() == "Alpha: Variant"

    second_tactic = grouped["Second"]
    assert [tech.id for tech in second_tactic] == ["TECH2"]


def test_grouping_can_exclude_subtechniques(atlas_module, sample_data):
    matrix = atlas_module.select_matrix(sample_data)
    grouped = atlas_module.group_techniques_by_tactic(
        matrix, include_subtechniques=False
    )
    assert [tech.id for tech in grouped["First"]] == ["TECH1", "TECH2"]


def test_grouping_handles_missing_collections(atlas_module):
    matrix = {
        "id": "ATLAS",
        "tactics": None,
        "techniques": None,
    }

    grouped = atlas_module.group_techniques_by_tactic(matrix)
    assert grouped == OrderedDict()


def test_select_matrix_rejects_invalid_collection(atlas_module):
    with pytest.raises(atlas_module.AtlasDataError):
        atlas_module.select_matrix({"matrices": "invalid"})


def test_summarise_matrix_counts(atlas_module, sample_data):
    matrix = atlas_module.select_matrix(sample_data)
    grouped = atlas_module.group_techniques_by_tactic(matrix)
    summary = atlas_module.summarise_matrix(grouped)
    assert isinstance(summary, OrderedDict)
    assert summary == OrderedDict([("First", 3), ("Second", 1)])


def test_load_atlas_data_rejects_missing_local_path(atlas_module, tmp_path):
    with pytest.raises(atlas_module.AtlasDataError):
        atlas_module.load_atlas_data(tmp_path / "missing.yaml")


def test_check_atlas_connection_uses_head(atlas_module, monkeypatch):
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return DummyResponse(status=200)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    assert atlas_module.check_atlas_connection(timeout=5.0) is True
    assert captured["timeout"] == 5.0
    request = captured["request"]
    assert request.get_method() == "HEAD"


def test_check_atlas_connection_supports_custom_url(atlas_module, monkeypatch):
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.get_full_url()
        captured["user_agent"] = request.get_header("User-agent")
        return DummyResponse(status=200)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    custom_url = "https://contoso.sharepoint.com/:u:/r/custom/ATLAS.yaml"
    assert atlas_module.check_atlas_connection(url=custom_url) is True
    assert captured["url"] == custom_url
    assert "pip/" in captured["user_agent"]


def test_check_atlas_connection_handles_http_error(atlas_module, monkeypatch):
    def fake_urlopen(request, timeout):
        return DummyResponse(status=500)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(atlas_module.AtlasDataError):
        atlas_module.check_atlas_connection()


def test_check_atlas_connection_handles_network_error(atlas_module, monkeypatch):
    def fake_urlopen(request, timeout):
        raise OSError("boom")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(atlas_module.AtlasDataError):
        atlas_module.check_atlas_connection()


def test_check_atlas_connection_falls_back_when_head_not_allowed(
    atlas_module, monkeypatch
):
    calls: list[tuple[object, float]] = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        if len(calls) == 1:
            raise HTTPError(request.full_url, 405, "Method Not Allowed", hdrs=None, fp=None)
        return DummyResponse(status=200)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    assert atlas_module.check_atlas_connection(timeout=2.5) is True
    head_request, head_timeout = calls[0]
    get_request, get_timeout = calls[1]
    assert head_request.get_method() == "HEAD"
    assert head_timeout == 2.5
    assert get_request.get_method() == "GET"
    assert get_request.get_header("Range") == "bytes=0-0"
    assert get_timeout == 2.5


def test_load_atlas_data_sets_user_agent(atlas_module, monkeypatch):
    captured_request: dict[str, object] = {}

    def fake_urlopen(request):
        captured_request["user_agent"] = request.get_header("User-agent")
        payload = b"matrices: []\n"
        return DummyDownloadResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    data = atlas_module.load_atlas_data("https://example.com/atlas.yaml")
    assert data == {"matrices": []}
    assert "pip/" in captured_request["user_agent"]


def test_import_fails_with_helpful_message(monkeypatch):
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name, package=None):  # pragma: no cover - invoked in test
        if name == "yaml":
            return None
        return original_find_spec(name, package)

    with monkeypatch.context() as m:
        m.setattr(importlib.util, "find_spec", fake_find_spec)
        sys.modules.pop("stop_azs.atlas", None)
        sys.modules.pop("stop_azs", None)
        with pytest.raises(ModuleNotFoundError) as exc:
            importlib.import_module("stop_azs.atlas")

    assert "pip install -r requirements.txt" in str(exc.value)
    importlib.reload(importlib.import_module("stop_azs.atlas"))
