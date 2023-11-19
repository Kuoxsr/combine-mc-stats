# combine-mc-stats
Consolidates several Java Edition statistics files into a single file.

## Why?
This project exists because [a streamer I watch regularly](https://www.twitch.tv/carlcrafts) discovered one night that his Minecraft statistics had reset and he was currently adding to a completely new set of stats, despite being in a hardcore world that was 5900+ "days" old.

Whether it was due to moving everything to a new PC or the installation of an update to the launcher or some other event that caused the stats to disappear, the problem he was facing was how to keep all the stats he had tallied-up over the last year+ of streaming without losing what had accumulated since the reset.

## What this script does
This script reads in two (or more) json files from a single folder, totals the values if the files share the same statistic, adds a statistic if the subsequent files have it but the previous file(s) don't, and creates an output file that contains the combination.

## Running the script
#### Environment
To run the script, you need a [python 3.11 environment](https://www.python.org/downloads/release/python-3110/).  Explaining [how to install](https://duckduckgo.com/?q=how+to+install+python+3.11) that is beyond the scope of this document.  The script imports the modules `argparse`, `json`, `pathlib` and `sys`.  To my knowledge, these are all built-in modules, and shouldn't require any extra installation.

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

Technically, I haven't tried more than two, but that _should_ work.  On the other hand, What's the scenario in which you would have more than two files that you would need to combine?

#### The command to run the script
One way to run the script is to copy the script to the folder that contains the files you want to combine.  With this method, it will already have the correct path, because you will have navigated there in your terminal to run the script:

```
[you@localhost:/path/to/target/folder]$ ./combine-mc-stats 
```

... or you can just pass that folder to the script via command-line parameter, like so:

```
[you@localhost:~]$ ./combine-mc-stats /path/to/target/folder 
```

I have not tested whether this script runs in a Windows environment, only Linux.  Your mileage may vary.  If you try it in Windows and it doesn't work, fix the problem and submit a pull request.  An issue in the bug tracker for that particular problem will likely go nowhere, because I do not own a copy of Windows in which to test.  If it _does_ work in Windows, let me know so that I can remove this paragraph.  It would also be helpful to let me know the proper syntax for that platform, so I can include examples for others.

## Output file
The final output file will be named `{UUID from the first file}.json`.  It will contain totals of all the stats that the two files share, and will contain all stats found in all files.  Put this file back into your `.minecraft/saves/{world name}/stats` folder, and you should be good to go, provided you didn't try to combine JSON files that contain something other than statistics.

#### Considerations
There is nothing preventing a user from renaming the output file to `.1.json` and simply running the script again and again to combine statistics up to the limits of integers (which might break the script - I haven't tried this.)

Also, I don't know how far back in Minecraft versions this script will work, since there have been many changes to the format of these files.  If you encounter something that doesn't work, submit a [bug report](https://github.com/Kuoxsr/combine-mc-stats/issues).

Thanks for your interest in my project!
