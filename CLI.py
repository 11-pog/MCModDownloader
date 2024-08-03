import argparse
import asyncio
from MCModDownloader import MCModDownloader
import concurrent.futures

if __name__ == "__main__":
    MCMD = MCModDownloader()

    parser = argparse.ArgumentParser(description="Download minecraft mods from Modrinth and Curseforge automatically (peak laziness)")

    input = parser.add_mutually_exclusive_group(required=True)
    input.add_argument("-m", "--mod-link", help="Single mod download, use a link", metavar="MOD LINK")
    input.add_argument("--ml", "--mod-list", help="Download a bunch of mods simultaneously", metavar="MOD LINKS", nargs="+")
    input.add_argument("--mltxt", "--mod-list-txt", help="Download the mods from a txt file containing one mod link per line", metavar="TXT FILE")

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

    elif args.ml is not None:
        for link in args.ml:
            name, mod = asyncio.run(MCMD.download_latest(link, parameters))
            asyncio.run(MCMD.saveFile(mod, name, args.output))

    else:
        try:
            with open(args.mltxt, 'r') as file:
                for line in file:
                    link = line.strip()

                    if link:
                        name, mod = asyncio.run(MCMD.download_latest(link, parameters))
                        asyncio.run(MCMD.saveFile(mod, name, args.output))
                    
        except FileNotFoundError:
            print(f"ERROR: Input file {args.mltxt} was not found")
        except Exception as e:
            print(f"An error occurred: {e}")

#def download_mod(url, params, output):
#    name, mod = asyncio.run(MCMD.download_latest(url, params))
#    asyncio.run(MCMD.saveFile(mod, name, output))
