import argparse
import asyncio
from MCModDownloader import MCModDownloader
import os



async def download_mod(url, params, output):
    try:
        name, mod = await MCMD.download_latest(url, params)
        await MCMD.saveFile(mod, name, output)
        print(f"sucessfully downloaded {name}")
        successful.append(f"- {name}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        failed.append(f"Failed to Download: {url}\n Cause: {e}")



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

    parser.add_argument("-o", "--output", help="Output directory for the mod", default="./output")

    args = parser.parse_args()
    
    parameters = {
        'game_versions': args.game_version,
        'loader': args.loader,
        'version_type': args.restrict
    }

    successful = []
    failed = []

    if args.mod_link is not None:
        asyncio.run(download_mod(args.mod_link, parameters, args.output))

    elif args.ml is not None:
        for link in args.ml:
            asyncio.run(download_mod(link, parameters, args.output))

    else:
        try:
            with open(args.mltxt, 'r') as file:                
                for line in file:
                    link = line.strip()

                    if link:
                        asyncio.run(download_mod(link, parameters, args.output))
                    
        except FileNotFoundError:
            print(f"ERROR: Input file {args.mltxt} was not found")
        except Exception as e:
            print(f"An error occurred: {e}")

    if len(successful) > 0:
        successfulPath = os.path.join(args.output, 'Successful_downloads.txt')
        with open(successfulPath, 'w') as f:
            f.write('\n'.join(successful))

    if len(failed) > 0:
        failedPath = os.path.join(args.output, 'Failed_downloads.txt')
        with open(failedPath, 'w') as f:
            f.write('\n'.join(failed))


