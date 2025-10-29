from __future__ import annotations

from collections import OrderedDict

import pytest

from stop_azs import (
    AtlasDataError,
    group_techniques_by_tactic,
    load_atlas_data,
    select_matrix,
    summarise_matrix,
)


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


def test_select_matrix_returns_expected_section(sample_data):
    matrix = select_matrix(sample_data)
    assert matrix["id"] == "ATLAS"


def test_grouping_includes_parent_tactic(sample_data):
    matrix = select_matrix(sample_data)
    grouped = group_techniques_by_tactic(matrix)
    assert list(grouped.keys()) == ["First", "Second"]

    first_tactic = grouped["First"]
    assert [tech.id for tech in first_tactic] == ["TECH1", "TECH1.A", "TECH2"]
    variant = first_tactic[1]
    assert variant.is_subtechnique is True
    assert variant.parent_id == "TECH1"
    assert variant.display_name() == "Alpha: Variant"

    second_tactic = grouped["Second"]
    assert [tech.id for tech in second_tactic] == ["TECH2"]


def test_grouping_can_exclude_subtechniques(sample_data):
    matrix = select_matrix(sample_data)
    grouped = group_techniques_by_tactic(matrix, include_subtechniques=False)
    assert [tech.id for tech in grouped["First"]] == ["TECH1", "TECH2"]


def test_summarise_matrix_counts(sample_data):
    matrix = select_matrix(sample_data)
    grouped = group_techniques_by_tactic(matrix)
    summary = summarise_matrix(grouped)
    assert isinstance(summary, OrderedDict)
    assert summary == OrderedDict([("First", 3), ("Second", 1)])


def test_load_atlas_data_rejects_missing_local_path(tmp_path):
    with pytest.raises(AtlasDataError):
        load_atlas_data(tmp_path / "missing.yaml")
