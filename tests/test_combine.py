"""Tests for combine-mc-stats."""
import json
import sys

import combine_mc_stats as combine

PLAYER_A = "11111111-1111-1111-1111-111111111111"
PLAYER_B = "22222222-2222-2222-2222-222222222222"


def write_stats(folder, uuid, session, stone, data_version=100):
    """Write one stats file, named ``{uuid}.{session}.json``, with a single statistic."""
    data = {
        "stats": {"minecraft:mined": {"minecraft:stone": stone}},
        "DataVersion": data_version,
    }
    (folder / f"{uuid}.{session}.json").write_text(json.dumps(data))


def run_script(folder, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["combine_mc_stats.py", str(folder)])
    combine.main()


def stone_of(path):
    return json.loads(path.read_text())["stats"]["minecraft:mined"]["minecraft:stone"]


def test_one_player_two_sessions_are_summed(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, session=1, stone=5)
    write_stats(tmp_path, PLAYER_A, session=2, stone=3)

    run_script(tmp_path, monkeypatch)

    assert stone_of(tmp_path / f"{PLAYER_A}.json") == 8


def test_two_players_are_not_mixed(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, session=1, stone=5)
    write_stats(tmp_path, PLAYER_A, session=2, stone=3)
    write_stats(tmp_path, PLAYER_B, session=1, stone=100)
    write_stats(tmp_path, PLAYER_B, session=2, stone=200)

    run_script(tmp_path, monkeypatch)

    assert stone_of(tmp_path / f"{PLAYER_A}.json") == 8
    assert stone_of(tmp_path / f"{PLAYER_B}.json") == 300
