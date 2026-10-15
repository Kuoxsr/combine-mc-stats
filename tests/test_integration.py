"""Tests for combine-mc-stats."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

import combine_mc_stats as combine

PLAYER_A = "11111111-1111-1111-1111-111111111111"
PLAYER_B = "22222222-2222-2222-2222-222222222222"


def write_stats(folder, uuid, session, stats, data_version=100):
    """Write one stats file, named ``{uuid}.{session}.json``."""
    (folder / f"{uuid}.{session}.json").write_text(
        json.dumps({"stats": stats, "DataVersion": data_version}),
    )


def run_script(folder, monkeypatch):
    monkeypatch.chdir(folder)      # the output directory is created in the cwd
    monkeypatch.setattr(sys, "argv", ["combine_mc_stats.py", str(folder)])
    combine.main()


def read_stats(path):
    return json.loads(path.read_text())


def read_output(folder, uuid):
    """Read a player's combined file from the output directory."""
    return read_stats(folder / combine.OUTPUT_DIRECTORY_NAME / f"{uuid}.json")


def test_one_player_two_sessions_are_summed(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, 1, {"minecraft:mined": {"minecraft:stone": 5}})
    write_stats(tmp_path, PLAYER_A, 2, {"minecraft:mined": {"minecraft:stone": 3}})

    run_script(tmp_path, monkeypatch)

    out = read_output(tmp_path, PLAYER_A)
    assert out["stats"]["minecraft:mined"]["minecraft:stone"] == 8


def test_two_players_are_not_mixed(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, 1, {"minecraft:mined": {"minecraft:stone": 5}})
    write_stats(tmp_path, PLAYER_A, 2, {"minecraft:mined": {"minecraft:stone": 3}})
    write_stats(tmp_path, PLAYER_B, 1, {"minecraft:mined": {"minecraft:stone": 100}})
    write_stats(tmp_path, PLAYER_B, 2, {"minecraft:mined": {"minecraft:stone": 200}})

    run_script(tmp_path, monkeypatch)

    out_a = read_output(tmp_path, PLAYER_A)
    out_b = read_output(tmp_path, PLAYER_B)
    assert out_a["stats"]["minecraft:mined"]["minecraft:stone"] == 8
    assert out_b["stats"]["minecraft:mined"]["minecraft:stone"] == 300


def test_values_are_capped_at_the_integer_limit(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, 1, {"minecraft:mined": {"minecraft:stone": 2_000_000_000}})
    write_stats(tmp_path, PLAYER_A, 2, {"minecraft:mined": {"minecraft:stone": 2_000_000_000}})

    run_script(tmp_path, monkeypatch)

    out = read_output(tmp_path, PLAYER_A)
    assert out["stats"]["minecraft:mined"]["minecraft:stone"] == 2_147_483_647


@pytest.mark.parametrize("index", [0, 1])
def test_an_orphaned_stat_survives_the_merge(tmp_path, monkeypatch, index):
    """A stat present in only one of the two files is kept in the output."""
    sessions = [
        {"minecraft:mined": {"minecraft:stone": 5}},      # session .1
        {"minecraft:mined": {"minecraft:stone": 5}},      # session .2
    ]
    sessions[index] = {"minecraft:crafted": {"minecraft:oak_door": 7}}   # the orphan

    write_stats(tmp_path, PLAYER_A, 1, sessions[0])
    write_stats(tmp_path, PLAYER_A, 2, sessions[1])

    run_script(tmp_path, monkeypatch)

    out = read_output(tmp_path, PLAYER_A)
    assert out["stats"]["minecraft:crafted"]["minecraft:oak_door"] == 7


def test_orphans_from_both_files_are_kept(tmp_path, monkeypatch):
    write_stats(tmp_path, PLAYER_A, 1, {
        "minecraft:mined":   {"minecraft:stone": 5},
        "minecraft:crafted": {"minecraft:oak_door": 3},   # orphan, only in .1
    })
    write_stats(tmp_path, PLAYER_A, 2, {
        "minecraft:mined":   {"minecraft:stone": 4},
        "minecraft:crafted": {"minecraft:torch": 9},      # orphan, only in .2
    })

    run_script(tmp_path, monkeypatch)

    out = read_output(tmp_path, PLAYER_A)
    assert out["stats"] == {
        "minecraft:mined":   {"minecraft:stone": 9},
        "minecraft:crafted": {"minecraft:oak_door": 3, "minecraft:torch": 9},
    }


def test_a_missing_path_exits_nonzero_and_reports_on_stderr(tmp_path):
    """A bad path must report on stderr and exit non-zero, like the other errors."""
    script = Path(__file__).resolve().parent.parent / "combine_mc_stats.py"

    result = subprocess.run(
        [sys.executable, str(script), str(tmp_path / "nope")],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 1
    assert "Specified path not found" in result.stderr
