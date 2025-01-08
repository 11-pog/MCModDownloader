# Minecraft Mod Downloader

## Note: This is still in Alpha, so things might not work as expected

## Important: This barely works now

A Python script to download Minecraft mods from Modrinth and Curseforge automatically.
Supports single mod downloads, batch downloads from a list, and dependency resolution (Auto download still WIP (i dont even know if i will actually finish it lmao))
Comes with free spaghetti code

## Disclaimer

We're not responsible for any damage caused by this package, including but not limited to:

- Brain damage
- Emotional Damage
- PseudoComa
- Spontaneous combustion
- High doses of radiation poisoning
- Deep Root Disease
- Spaghettification
- Non-Existence
- Enlightenment
- *Death*

### Requirements

- Python 3.11 or later
- Pip

## How to use

### Installation

Note: These installation steps are temporary until the package is released on PyPI.

1. Download PIP if you still dont have it (a little complicated, recommended searching for youtube tutorials if you dont know how to)
2. Go into the **Releases** section and download the most recent version of the tarball (0.1.a.tar.gz at the time).
3. Open a terminal or command prompt and navigate to the directory in which you downloaded the tarball.
4. Run the following command: "pip install [path to the tarball]".

### Setting up

- go to [The official CurseForge dev console](https://console.curseforge.com/#%2Fapi-keys) to get a curseforge api key
- Open your cmd, and type "mcmm -c cf-api-key [the key you received]"
- As simple as that

### Usage

General usage: Use "mcmm" as a prefix to run a command, then add the arguments (e.g: -m [mod link], -g 1.20.1, etc)

#### Basic downloads

- Open the cmd/powershell in the directory you want to output the files
- Type "mcmm -m [Mod Link] [other parameters]" for basic, single mod download from a url
- Type "mcmm -ml [Link1, Link2, ...] [other parameters]" for multiple downloads, separating each url with a space
- Type "mcmm -mlt [Path to the txt] [other parameters]" to download multiple mods at the same time using a txt file with a single mod url per line

#### Mod Filtering Parameters

- "-g [game version]" - to specify a game version
- "-l [mod loaders]" - to specify a single or multiple mod loaders (defaults to forge and neoforge)
- "-r [version type]" - **DEPRECATED:** to specify the type of version to the mod (Release, Beta, Alpha). Note that this parameter is broken and may not work with CurseForge links.

#### Some extra commands

- "-o" - optional output directory, default can be configured in '--configs'
- "-c" - set configurations, refer to configs for more info
- "-h" or "--help" - prints all commands with a detailed description (and aliases/long versions)

#### **WIP:** Dependency resolution

- "-rd" - **Not implemented:** Attempts to resolve any cached missing dependencies.
- "-bl" - **Not implemented:** Automatically blacklists any dependencies removed with -rw
- "-rw" - Opens the missing dependencies file for manual review and editing

### Configs

Here are the configurations (-c) currently implemented:

- Api Specific:
  - *cf-api-key [Api key]* -> configures the curseforge api key
- General
  - *default-output-dir [directory path]* -> Sets the default output directory when the -o parameter is not specified. You can enter a valid directory path, 'cwd', or './'
    - 'cwd' sets the default output directory to the current working directory of the script **at runtime**, which means it will change depending on the directory from which the script is run. For example, if you run the script in D:/Videos, the default output directory will be D:/Videos, and if you run it in C:/Images, the default output directory will be C:/Images.
    - './' sets the default output directory to the **absolute path** of the current working directory **at the time the setting is configured**, which means it will remain fixed even if the script is run from a different directory. For example, if you set 'default-output-dir ./' while running the script in C:/Images, the default output directory will always be C:/Images, even if you run the script in D:/Videos later.
  - *default-mod-loader [loader] [additional loaders] -> sets the default mod loaders for this package
    - Can be: Forge, Neoforge, Fabric, and/or Quilt
- Other
  - *prioritize-cf [True or False]* -> Sets if the MissingDependencies.txt will prioritize Curseforge or Modrinth links.

### Output

The script create two folders in the output directory:

- "mods", which has the downloaded mods
- "results", which holds some txt files with the results

The txts in the results folder can be:

- "Successful_downloads.txt", stores the name of every successfully downloaded mod
- "Failed_downloads.txt", stores the modlinks and the cause of every failed mod download
- "MissingDependencies.txt", store the name of any missing dependency in case the script detects any, does not auto donwload yet (might implement, but still not sure)

## License and Copyright Information

### Copyright

This software is licensed under the MIT License
