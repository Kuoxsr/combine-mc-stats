"""Tests for combine-mc-stats."""
import json
import sys

import combine_mc_stats as combine

PLAYER_A = "11111111-1111-1111-1111-111111111111"
PLAYER_B = "22222222-2222-2222-2222-222222222222"


def write_stats(folder, uuid, session, stats, data_version=100):
    """Write one stats file, named ``{uuid}.{session}.json``."""
    (folder / f"{uuid}.{session}.json").write_text(
        json.dumps({"stats": stats, "DataVersion": data_version})
    )


def run_script(folder, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["combine_mc_stats.py", str(folder)])
    combine.main()


def read_stats(path):
    return json.loads(path.read_text())


def test_one_player_two_sessions_are_summed(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, 1, {"minecraft:mined": {"minecraft:stone": 5}})
    write_stats(tmp_path, PLAYER_A, 2, {"minecraft:mined": {"minecraft:stone": 3}})

    run_script(tmp_path, monkeypatch)

    out = read_stats(tmp_path / f"{PLAYER_A}.json")
    assert out["stats"]["minecraft:mined"]["minecraft:stone"] == 8


def test_two_players_are_not_mixed(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, 1, {"minecraft:mined": {"minecraft:stone": 5}})
    write_stats(tmp_path, PLAYER_A, 2, {"minecraft:mined": {"minecraft:stone": 3}})
    write_stats(tmp_path, PLAYER_B, 1, {"minecraft:mined": {"minecraft:stone": 100}})
    write_stats(tmp_path, PLAYER_B, 2, {"minecraft:mined": {"minecraft:stone": 200}})

    run_script(tmp_path, monkeypatch)

    out_a = read_stats(tmp_path / f"{PLAYER_A}.json")
    out_b = read_stats(tmp_path / f"{PLAYER_B}.json")
    assert out_a["stats"]["minecraft:mined"]["minecraft:stone"] == 8
    assert out_b["stats"]["minecraft:mined"]["minecraft:stone"] == 300


def test_values_are_capped_at_the_integer_limit(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, 1, {"minecraft:mined": {"minecraft:stone": 2_000_000_000}})
    write_stats(tmp_path, PLAYER_A, 2, {"minecraft:mined": {"minecraft:stone": 2_000_000_000}})

    run_script(tmp_path, monkeypatch)

    out = read_stats(tmp_path / f"{PLAYER_A}.json")
    assert out["stats"]["minecraft:mined"]["minecraft:stone"] == 2_147_483_647
