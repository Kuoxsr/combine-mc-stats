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
