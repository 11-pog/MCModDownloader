import argparse
import asyncio
from MCModDownloader import MCModDownloader, MCM_Utils
from MCSiteAPI import ModrinthAPI
from MCSiteAPI import CurseforgeAPI
import os

MCMD = MCModDownloader()
MRAPI = ModrinthAPI()
CFAPI = CurseforgeAPI()
MCUtils = MCM_Utils()

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
        downloadedIdList.append({'data': metadata['modId'], 'host': host} if host == "www.curseforge.com"
                                else {'data': metadata['project_id'], 'host': host})
        
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
            print("Missing Dependencies FOUND")
            print(missingDependencies)

            if mainArguments.dd:
                pass #WIP PLACEHOLDER
            else:
                txtfile = [
                    (await MRAPI.get_project_by_id(dep[0], retries=20))['title'] if dep[0] is not None
                       else (await CFAPI.get_project_by_id(dep[1]))['name']
                    for dep in missingDependencies
                ]
                
                dependencyPath = os.path.join(mainArguments.output, 'MissingDependencies.txt')
                with open(dependencyPath, 'w') as f:
                    f.write("- " + "\n- ".join(txtfile))

                await MCMD.returnModName(dependencyIdList[0]['data'], dependencyIdList[0]['host'])


    if len(dependencyIdList) > 0:
        print("dependencies detected, checking for any missing")

        seen = set()
        requiredDependencies = [
            [data, dep['host']] 
            for dep in dependencyIdList
            for data in dep['data']
            if  ((dep['host'] == 'www.curseforge.com' and data['relationType'] == 3) or
                (dep['host'] == 'modrinth.com' and data['dependency_type'] == 'required')) and
                tuple(sorted(data.items())) + (dep['host'],) not in seen and not seen.add(tuple(sorted(data.items())) + (dep['host'],))
        ]

        equivalentDependencyIds = []

        async def dependencyAppendId(data, host):
            ids = await MCUtils.get_equivalent_ids(data, host)
            equivalentDependencyIds.append(ids)

        tasks = []
        for data, host in requiredDependencies:
            tasks.append(dependencyAppendId(data, host))
        
        await asyncio.gather(*tasks)

        missingDependencies = [
            dependency for dependency in equivalentDependencyIds
            if not any(value in [id['data'] for id in downloadedIdList] for value in dependency)
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
