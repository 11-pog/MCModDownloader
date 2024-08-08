# Minecraft Mod Downloader

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
- Enlightment
- *Death*

### Requirements

- Python 3.11 or later
- Pip
- Some packages there
- A enviroment variable with a Curseforge api key (name "CF_API_KEY") (i seriously need to change this to something more )

## How to use

### Installation

- Download the tar.gz from this repo
- Run "pip install [path to the tarball]"
- Thats it lmao

### Usage

#### Basic downloads

- Open the cmd/powershell in the directory you want to output the files
- Type "mcmm -m [Mod Link]" for basic, single mod download
- Type "mcmm --ml [Link1, Link2, ...]" for multiple downloads
- Type "mcmm --dltxt [Path to the txt]" to download multiple mods at the same time using a txt file with a single mod url per line

#### Some parameters to get the right mods

- "-g [game version]" to specify a game version
- "-l [mod loaders]" to specify a single or multiple mod loaders (defaults to forge and neoforge)
- "-r [version type]" to specify the type of version to the mod (Release, Beta, Alpha)(Might not work with curseforge links)(Some mods only have beta or alphas, so it is not recommended to add this)

#### Some extra parameters

- "-d" does nothing, supposed to auto download any dependency if it exists, however currently does nothing
- "-o" optional output directory, always defaults to the folder you're in

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
