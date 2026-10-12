#!/usr/bin/env python3

"""
Problem: Automatically combine multiple Minecraft statistics files,
in the event that they get cleared for some reason, and you don't realize
until you have more stats in a second file.
Target Users: Me/Us
Target System: GNU/Linux/Unix/Mac
Interface: Command-line
Functional Requirements: Take a set of statistics json files and combine the totals within them
Notes:

    Since the files we're interested in are named with a UUID representing the player, all stats
    files for a given player will have exactly the same name.  Due to this, I propose that we add

    ".X" before ".json"

    ... where .X is a sequence number to differentiate each file from the others

    In my test folder, I have used a randomized UUID

    Make sure that the target folder only has the renamed files in it

Command-line arguments:

    --help      (-h)    Show usage
    --version   (-v)    Show version number
"""

__version__ = '0.3'
__maintainer__ = "kuoxsr@gmail.com"
__status__ = "Prototype"

# Import modules
from pathlib import Path
import argparse
import json
import sys


def handle_command_line():
    """
    Handle arguments supplied by the user
    """

    parser = argparse.ArgumentParser(
        prog="Sound Pack Checker",
        description="generates lists of invalid connections between json and sound files.")

    parser.add_argument("-v", "--version", action="version", version="%(prog)s version " + __version__)

    parser.add_argument(
        "path",
        action="store",
        nargs=argparse.REMAINDER,
        help="Path to the sounds.json file you want to check.  The file name itself is not required.")

    args = parser.parse_args()

    # path is a LIST at this point, and we want just a string
    if len(args.path) > 0:
        args.path = args.path[0]
    else:
        args.path = ""

    # If the user doesn't specify a path, use current working directory
    if not args.path:
        args.path = Path.cwd()

    # If the user specifies a string, make sure it's a path object
    path = Path(args.path)

    # Does path folder exist on the file system?
    if not path.exists():
        print(f"Specified path not found. {path} is not a valid filesystem path.")
        exit()

    # Finally, make the argument a Path  (does this work?)
    args.path = Path(args.path).resolve()

    # print(f"args: {args}"); exit()
    return args


def read_stats(path: Path) -> dict:
    """Load one stats file."""
    with open(path, "r") as file:
        return dict(json.load(file))


def write_stats(path: Path, data: dict) -> None:
    """Write one stats file."""
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def player_uuid(path: Path) -> str:
    """Return the player UUID from a stats filename like {UUID}.X.json."""
    name, dot, sequence = path.stem.partition(".")

    if not dot:
        sys.exit(f"\nError: Aborting script.   {path.name} has unexpected name.\n"
                 f"       Valid name format: {{UUID}}.X.json, where X is a sequence number.")

    return name


def merge_stats(files: list[Path]) -> dict:
    """Merge a player's stats files, summing values and keeping the highest DataVersion."""
    output_json: dict[str, dict[str, dict[str, int]] | int] = {"stats": {}, "DataVersion": 0}

    for file in files:
        data: dict[str, dict[str, dict[str, int]] | int] = read_stats(file)

        # Always keep the highest DataVersion number
        if data["DataVersion"] > output_json["DataVersion"]:
            output_json["DataVersion"] = data["DataVersion"]

        # Loop through the outer keys (categories such as "crafted" or "broken" or "mined")
        for outer_key, stats in data["stats"].items():
            output_json["stats"][outer_key] = merge_category(
                output_json["stats"].get(outer_key, {}), stats)

    return output_json


def merge_category(target: dict[str, int], source: dict[str, int]) -> dict[str, int]:
    """Merge one stats category: sum every item's count, capped, into a new dict."""
    merged = dict(target)
    for key, value in source.items():
        merged[key] = cap(merged.get(key, 0) + value)
    return merged


def cap(value: int) -> int:
    """Clamp a stat to the largest value a Minecraft counter can hold."""
    return min(value, 2_147_483_647)


def find_sessions(directory: Path) -> tuple[list[Path], list[Path]]:
    """Return the ``.1`` and ``.2`` stats files under directory, each sorted."""
    return (sorted(directory.rglob("*.1.json")),
            sorted(directory.rglob("*.2.json")))


def pair_by_uuid(ones: list[Path], twos: list[Path]) -> list[tuple[Path, Path]]:
    """Pair each ``.1`` file with the ``.2`` file that shares its player UUID."""
    pairs = []
    for one in ones:
        for two in twos:
            if player_uuid(one) == player_uuid(two):
                pairs.append((one, two))
                break        # each player has at most one .2, so stop searching
    return pairs


def combine(directory: Path) -> None:
    """Combine every player's stats files under directory, one output each."""
    json_files: list[Path] = sorted([f for f in directory.rglob('*.json')])
    if len(json_files) == 0:
        sys.exit(f"\nError: There are no JSON files under {directory}")

    json1_files, json2_files = find_sessions(directory)
    print()
    print(f"Combining from {len(json1_files)} old files and {len(json2_files)} new files")

    matches = 0
    for file1, file2 in pair_by_uuid(json1_files, json2_files):
        uuid = player_uuid(file1)
        print(f"{uuid} Match found")
        matches += 1

        output_json = merge_stats([file1, file2])
        output_file_path = directory / f"{uuid}.json"
        write_stats(output_file_path, output_json)

    print(f"Matched {matches} files")


# Main -------------------------------------------------
def main():
    """
    Main program loop
    """
    args = handle_command_line()
    combine(args.path)


# ------------------------------------------------------
# Main program loop
# ------------------------------------------------------

# Run main program loop only if not called as a module
if __name__ == "__main__":
    main()