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


def test_pair_by_uuid_matches_1_and_2_files(tmp_path):
    a1 = tmp_path / "aaa.1.json"
    a2 = tmp_path / "aaa.2.json"
    b1 = tmp_path / "bbb.1.json"
    b2 = tmp_path / "bbb.2.json"
    c1 = tmp_path / "ccc.1.json"          # c has no .2, so it pairs with nothing

    assert combine.pair_by_uuid([a1, b1, c1], [a2, b2]) == [(a1, a2), (b1, b2)]


def test_combine_writes_a_merged_file_per_player(tmp_path):
    combine.write_stats(tmp_path / "a.1.json", {"stats": {"minecraft:mined": {"minecraft:stone": 5}}, "DataVersion": 100})
    combine.write_stats(tmp_path / "a.2.json", {"stats": {"minecraft:mined": {"minecraft:stone": 3}}, "DataVersion": 100})

    combine.combine(tmp_path)

    out = combine.read_stats(tmp_path / "a.json")
    assert out["stats"]["minecraft:mined"]["minecraft:stone"] == 8


def test_combine_exits_when_there_are_no_json_files(tmp_path):
    with pytest.raises(SystemExit):
        combine.combine(tmp_path)


def test_cap_clamps_at_the_integer_limit():
    assert combine.cap(2_147_483_646) == 2_147_483_646
    assert combine.cap(2_147_483_647) == 2_147_483_647
    assert combine.cap(2_147_483_648) == 2_147_483_647
    assert combine.cap(9_000_000_000) == 2_147_483_647
