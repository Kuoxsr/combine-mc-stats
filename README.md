# combine-mc-stats
Consolidates Java Edition statistics files: for one player, or for several players at once.

## Why?
This project exists because [a streamer I watch regularly](https://www.twitch.tv/carlcrafts) discovered one night that his Minecraft statistics had reset and he was currently adding to a completely new set of stats, despite being in a hardcore world that was 5900+ "days" old.

Whether it was due to moving everything to a new PC or the installation of an update to the launcher or some other event that caused the stats to disappear, the problem he was facing was how to keep all the stats he had tallied-up over the last year+ of streaming without losing what had accumulated since the reset.

## What this script does
This script reads every statistics file in a folder and combines them **per player**.  Give it one player's files and it writes one combined file.  Give it the files for several players and it writes one combined file for each, keeping the players separate.

Values are summed where the files share a statistic, and where they don't, the orphaned statistic is included in the combined file just as it was in the original.  No statistic left behind! 🛡️

_So a whole server's-worth of players can be recombined in a single pass, rather than one player at a time._

>[!IMPORTANT]
>The files have to be renamed first, so that two files for the same player can sit in one folder together.  That is covered in [Target folder and file naming convention](#target-folder-and-file-naming-convention) below.

The multi-player support came from a pull request by [Jacklynn](https://github.com/jacklynn-yan).  My very first pull request ever! 🥳🎉

## Running the script
#### Environment  <img height="24px" width="24px" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" />
The [Python](https://www.python.org/) version that this project uses is pinned in `mise.toml`, so installing [mise](https://mise.jdx.dev) and running `mise install` gives you the right interpreter.  The script imports only built-in modules: `argparse`, `json`, `pathlib`, `sys` and `typing`, so there is nothing else to install in order to run it.

#### Target folder and file naming convention
Before running this script, find the files you want to combine and put them into a temporary folder that you create specifically for this process.

You will find the statistics files in the following folders:
```
{current Minecraft instance path}/.minecraft/saves/{world name}/stats
{backup Minecraft instance path}/.minecraft/saves/{world name}/stats
```

Because the files are named `{user's UUID}.json`, the backup file and the current file will both be the exact same name.  In order to put them into the same folder, they need new names.  This script expects them to be named like this:

```
{user's UUID}.1.json
{user's UUID}.2.json
etc
```

The script combines each player's `.1` and `.2` files.  Combining more than two files for a single player is not supported yet.

#### The command to run the script
One way to run the script is to copy the script to the folder that contains the files you want to combine.  With this method, it will already have the correct path, because you will have navigated there in your terminal to run the script:

```
[you@localhost:/path/to/target/folder]$ ./combine_mc_stats.py 
```

... or you can just pass that folder to the script via command-line parameter, like so:

```
[you@localhost:~]$ ./combine_mc_stats.py /path/to/target/folder 
```

I have not tested whether this script runs in a Windows environment, only Linux.  Your mileage may vary.  If you try it in Windows and it doesn't work, fix the problem and submit a pull request.  An issue in the bug tracker for that particular problem will likely go nowhere, because I do not own a copy of Windows in which to test.  If it _does_ work in Windows, let me know so that I can remove this paragraph.  It would also be helpful to let me know the proper syntax for that platform, so I can include examples for others.

## Output file
The script writes one file per player, named `{UUID}.json`.  Each one contains the totals of that player's `.1` and `.2` files.  Put it back into your `.minecraft/saves/{world name}/stats` folder, and you should be good to go, provided you didn't try to combine JSON files that contain something other than statistics.

#### Considerations
There is nothing preventing a user from renaming the output file to `.1.json` and simply running the script again and again to combine statistics up to the limits of integers (which might break the script - I haven't tried this.)

Also, I don't know how far back in Minecraft versions this script will work, since there have been many changes to the format of these files.  If you encounter something that doesn't work, submit a [bug report](https://github.com/Kuoxsr/combine-mc-stats/issues).

Thanks for your interest in my project!  🥰

---
## Testing (for developers)

The tests use [pytest](https://pytest.org).  They build their own sample statistics files in a temporary folder, so they never touch your real stats.

The environment is declared in two files: `mise.toml` pins the Python version and defines the tasks, and `pyproject.toml` declares pytest as a dev dependency and holds the lint configuration.

The linter is [Ruff](https://docs.astral.sh/ruff/), configured under `[tool.ruff]` in `pyproject.toml`.  It selects every rule and then disables the ones this project declines, so each exception is recorded next to its reason.

```bash
mise install        # install the pinned Python
mise run setup      # create .venv and install pytest
mise run tests      # run the suite
```

The long form, if you would rather not use mise's tasks:

```bash
python -m venv .venv
.venv/bin/pip install --group dev
.venv/bin/pytest
```

