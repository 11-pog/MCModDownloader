import argparse
import asyncio
from MCModDownloader import MCModDownloader

if __name__ == "__main__":
    MCMD = MCModDownloader()

    parser = argparse.ArgumentParser(description="Mod Downloader")

    input = parser.add_mutually_exclusive_group(required=True)
    input.add_argument("--ml", "--mod-list", help="List of mods to download, based on a .txt file with the links", metavar="MODS.TXT")
    input.add_argument("-m", "--mod-link", help="Single mod download, use a link", metavar="MOD LINK")

    parser.add_argument("-g", "--game-version", help="Version of minecraft for the mod (eg: 1.19.2, 1.20.1, etc)", nargs='+')
    parser.add_argument("-l", "--loader", help="The mod loader for this mod (eg: forge, neoforge, fabric)", default=["forge"], nargs='+')
    parser.add_argument("-r", "--restrict", help='Restricts mod to specific version types', choices=["Release", "Beta", "Alpha"], nargs='+')

    parser.add_argument("-o", "--output", help="Output directory for the mod", default="./mods")

    args = parser.parse_args()
    
    parameters = {
        'game_versions': args.game_version,
        'loader': args.loader,
        'version_type': args.restrict
    }

    if args.mod_link is not None:
        name, mod = asyncio.run(MCMD.download_latest(args.mod_link, parameters))
        asyncio.run(MCMD.saveFile(mod, name, args.output))

    #Mod list is WIP
