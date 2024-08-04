import argparse
import asyncio
from MCModDownloader import MCModDownloader
from MCSiteAPI import ModrinthAPI
from MCSiteAPI import CurseforgeAPI
import os

MCMD = MCModDownloader()
MRAPI = ModrinthAPI()
CFAPI = CurseforgeAPI()

successful = []
failed = []

downloadedIdList = []
dependencyIdList = []


async def download_mod(url, params, output):
    try:
        name, mod, metadata, host = await MCMD.download_latest(url, params)
        await MCMD.saveFile(mod, name, output)
        print(f"sucessfully downloaded {name}")
        successful.append(f"{name}")
        downloadedIdList.append({'data': metadata['id'], 'host': host})

        if len(metadata['dependencies']) > 0:
            dependencyIdList.append({'data': metadata['dependencies'], 'host': host})

    except Exception as e:
        print(f"Error downloading {url}: {e}")
        failed.append(f"Failed to Download: {url}\nCause: {e}")




async def multi_download(txtfile, params, output):
    try:
        with open(txtfile, 'r') as file:      
            task = []
            for line in file:
                link = line.strip()
                if link:
                    task.append(download_mod(link, params, output))
                    #await download_mod(link, parameters, args.output)
            await asyncio.gather(*task)
                    
    except FileNotFoundError:
        print(f"ERROR: Input file {txtfile} was not found")
    except ValueError as e:
        print(f"An error occurred: {e}")




async def main(mainArguments):   
    parameters = {
        'game_versions': [mainArguments.game_version],
        'loader': mainArguments.loader,
        'version_type': mainArguments.restrict
    }


    if mainArguments.mod_link is not None:
        await download_mod(mainArguments.mod_link, parameters, mainArguments.output)

    elif mainArguments.ml is not None:
        for link in mainArguments.ml:
            await download_mod(link, parameters, mainArguments.output)

    else:
        await multi_download(mainArguments.mltxt, parameters, mainArguments.output)


    if len(successful) > 0:
        successfulPath = os.path.join(mainArguments.output, 'Successful_downloads.txt')
        successful.sort()
        with open(successfulPath, 'w') as f:
            f.write('- ' + '\n- '.join(successful))


    if len(failed) > 0:
        failedPath = os.path.join(mainArguments.output, 'Failed_downloads.txt')
        with open(failedPath, 'w') as f:
            f.write('\n'.join(failed))


    async def dependencyHandler(missingDependencies):
        if len(missingDependencies) > 0:
            if mainArguments.dd:
                pass #WIP PLACEHOLDER
            else:
                print(missingDependencies)
                dependencyPath = os.path.join(mainArguments.output, 'MissingDependencies.txt')
                txtfile = []

                await MCMD.returnModName(dependencyIdList[0]['data'], dependencyIdList[0]['host'])


    if len(dependencyIdList) > 0:
        missingDependencies = [
            dependency['data'] for dependency in dependencyIdList
            if dependency['data'] not in [id['data'] for id in downloadedIdList]
        ]
        await dependencyHandler(missingDependencies)


    




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download minecraft mods from Modrinth and Curseforge automatically (peak laziness)")

    input = parser.add_mutually_exclusive_group(required=True)
    input.add_argument("-m", "--mod-link", help="Single mod download, use a link", metavar="MOD LINK")
    input.add_argument("--ml", "--mod-list", help="Download a bunch of mods simultaneously", metavar="MOD LINKS", nargs="+")
    input.add_argument("--mltxt", "--mod-list-txt", help="Download the mods from a txt file containing one mod link per line", metavar="TXT FILE")

    parser.add_argument("-g", "--game-version", help="Version of minecraft for the mod (eg: 1.19.2, 1.20.1, etc)")
    parser.add_argument("-l", "--loader", help="The mod loader for this mod (eg: forge, neoforge, fabric)", default=["forge", "neoforge"], nargs='+')
    parser.add_argument("-r", "--restrict", help='Restricts mod to specific version types', choices=["Release", "Beta", "Alpha"], nargs='+')
    parser.add_argument("-d", "--dd", help="Auto downloads any missing dependencies", action="store_true")

    parser.add_argument("-o", "--output", help="Output directory for the mod", default="./output")

    try:
        args = parser.parse_args()
        asyncio.run(main(args))
    except SystemExit:
        print("Invalid commands or missing required commands, use --help to see the command list")
