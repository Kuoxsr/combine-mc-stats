"""Unit tests for the functions in combine_mc_stats."""
import json

import combine_mc_stats as combine


def test_read_stats_loads_a_file(tmp_path):
    path = tmp_path / "stats.json"
    path.write_text(json.dumps({"stats": {"minecraft:mined": {"minecraft:stone": 5}}, "DataVersion": 42}))

    assert combine.read_stats(path) == {
        "stats": {"minecraft:mined": {"minecraft:stone": 5}},
        "DataVersion": 42,
    }
