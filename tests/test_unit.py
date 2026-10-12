"""Unit tests for the functions in combine_mc_stats."""
import json
from pathlib import Path

import pytest

import combine_mc_stats as combine


def test_read_stats_loads_a_file(tmp_path):
    path = tmp_path / "stats.json"
    path.write_text(json.dumps({"stats": {"minecraft:mined": {"minecraft:stone": 5}}, "DataVersion": 42}))

    assert combine.read_stats(path) == {
        "stats": {"minecraft:mined": {"minecraft:stone": 5}},
        "DataVersion": 42,
    }


def test_write_stats_writes_a_file(tmp_path):
    path = tmp_path / "stats.json"

    combine.write_stats(path, {"stats": {"minecraft:mined": {"minecraft:stone": 5}}, "DataVersion": 42})

    assert json.loads(path.read_text()) == {
        "stats": {"minecraft:mined": {"minecraft:stone": 5}},
        "DataVersion": 42,
    }


def test_player_uuid_extracts_the_uuid():
    path = Path("11111111-1111-1111-1111-111111111111.1.json")

    assert combine.player_uuid(path) == "11111111-1111-1111-1111-111111111111"


def test_player_uuid_rejects_a_name_without_a_sequence():
    path = Path("11111111-1111-1111-1111-111111111111.json")

    with pytest.raises(SystemExit):
        combine.player_uuid(path)


def test_merge_stats_sums_values(tmp_path):
    combine.write_stats(tmp_path / "a.1.json", {"stats": {"minecraft:mined": {"minecraft:stone": 5}}, "DataVersion": 100})
    combine.write_stats(tmp_path / "a.2.json", {"stats": {"minecraft:mined": {"minecraft:stone": 3}}, "DataVersion": 100})

    merged = combine.merge_stats([tmp_path / "a.1.json", tmp_path / "a.2.json"])

    assert merged["stats"]["minecraft:mined"]["minecraft:stone"] == 8


@pytest.mark.parametrize(
    "versions",
    [(100, 3578), (3578, 100)],
    ids=["highest last", "highest first"],
)
def test_merge_stats_keeps_the_highest_data_version(tmp_path, versions):
    first, second = versions
    combine.write_stats(tmp_path / "a.1.json", {"stats": {"minecraft:mined": {"minecraft:stone": 5}}, "DataVersion": first})
    combine.write_stats(tmp_path / "a.2.json", {"stats": {"minecraft:mined": {"minecraft:stone": 5}}, "DataVersion": second})

    merged = combine.merge_stats([tmp_path / "a.1.json", tmp_path / "a.2.json"])

    assert merged["DataVersion"] == max(versions)


def test_find_sessions_gathers_the_1_and_2_files(tmp_path):
    combine.write_stats(tmp_path / "a.1.json", {"stats": {}, "DataVersion": 1})
    combine.write_stats(tmp_path / "a.2.json", {"stats": {}, "DataVersion": 1})
    combine.write_stats(tmp_path / "b.1.json", {"stats": {}, "DataVersion": 1})

    ones, twos = combine.find_sessions(tmp_path)

    assert ones == [tmp_path / "a.1.json", tmp_path / "b.1.json"]
    assert twos == [tmp_path / "a.2.json"]
