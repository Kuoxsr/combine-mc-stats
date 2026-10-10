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


# Main -------------------------------------------------
def main():
    """
    Main program loop
    This function generates a sounds.json file from a folder structure of .ogg files
    """

    args = handle_command_line()

    target: Path = args.path
    # print(f"target: {target}")
    # exit()
    
    data_version: int = 0
    uuid: str = ""

    # For each json stats file in the target folder
    json_files: list[Path] = sorted([f for f in target.rglob('*.json')])
    files_found = len(json_files)
    if files_found == 0:
        sys.exit(f"\nError: There are no JSON files under {target}")

    json1_files: list[Path] = sorted([f for f in target.rglob('*.1.json')])
    json2_files: list[Path] = sorted([f for f in target.rglob('*.2.json')])
    print()
    
    print(f"Combining from {len(json1_files)} old files and {len(json2_files)} new files")
    matches = 0

    for file1 in json1_files:

        # Capture the UUID from the first file
        suffix1 = file1.suffix[0]

        if suffix1 not in file1.stem:
            sys.exit(f"\nError: Aborting script.   {file1.name} has unexpected name.\n"
                     f"       Valid name format: {{UUID}}.X.json, where X is a sequence number.")

        index1 = file1.stem.index(suffix1)
        uuid1 = file1.stem[:index1]

        for file2 in json2_files:
            suffix2 = file2.suffix[0]

            if suffix2 not in file2.stem:
                sys.exit(f"\nError: Aborting script.   {file2.name} has unexpected name.\n"
                        f"       Valid name format: {{UUID}}.X.json, where X is a sequence number.")

            index2 = file2.stem.index(suffix2)
            uuid2 = file2.stem[:index2]

            if uuid1 == uuid2:
                print(f"{uuid1} Match found")
                matches += 1
                matched_files = [file1, file2]

                output_json: dict[str, dict[str, dict[str, int]] | int] = {"stats": {}, "DataVersion": 0}

                for file in matched_files:
                    # deserialize json data
                    with open(file, "r") as read_file:
                        data: dict[str, dict[str, dict[str, int]] | int] = dict(json.load(read_file))
                        # print(f"data: {data}")

                    # Always keep the highest DataVersion number
                    if data["DataVersion"] > output_json["DataVersion"]:
                        output_json["DataVersion"] = data["DataVersion"]

                    # Loop through the outer keys (categories such as "crafted" or "broken" or "mined")
                    for outer_key in data["stats"]:

                        # Create outer key if it doesn't already exist
                        if outer_key not in output_json["stats"]:
                            output_json["stats"][outer_key] = {}
                            # print(f"outer_key: {outer_key}")

                        # Loop through the inner keys (actual minecraft items)
                        for inner_key, value in data["stats"][outer_key].items():

                            # Create inner key if it doesn't already exist
                            if inner_key not in output_json["stats"][outer_key]:
                                output_json["stats"][outer_key][inner_key] = 0
                                # print(f"inner_key: {inner_key} -> {data['stats'][outer_key][inner_key]}")

                            output_json["stats"][outer_key][inner_key] += value

                            # Currently, Minecraft loses its mind if values are larger than 2,147,483,647
                            if output_json["stats"][outer_key][inner_key] >= 2_147_483_647:
                                output_json["stats"][outer_key][inner_key] = 2_147_483_647

                # Build the output file's name using the discovered UUID
                output_file_path = target / f"{uuid1}.json"

                # Write the output file to the target folder
                with open(output_file_path, "w") as fp:
                    json.dump(output_json, fp, indent=4)

    print(f"Matched {matches} files")

    # print(f"\n{output_file_path.name}\nFile created in {target} with the following contents:\n")
    # print(json.dumps(output_json, indent=4))


# ------------------------------------------------------
# Main program loop
# ------------------------------------------------------

# Run main program loop only if not called as a module
if __name__ == "__main__":
    main()