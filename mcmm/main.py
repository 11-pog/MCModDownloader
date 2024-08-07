# main.py

import argparse
import asyncio
from MCModDownloader import MCModDownloader
from MCM_Utils import MCM_Utils
from MCSiteAPI import ModrinthAPI, CurseforgeAPI
import os

MCMD = MCModDownloader()
MRAPI = ModrinthAPI()
CFAPI = CurseforgeAPI()
MCUtils = MCM_Utils()

successful = []
failed = []

downloadedIdList = []
dependencyIdList = []

async def main(mainArguments):   
    parameters = {
        'game_versions': [mainArguments.game_version],
        'loader': mainArguments.loader,
        'version_type': mainArguments.restrict
    }


    if mainArguments.mod_link is not None:
        failedStatus, result, dlid, dpid = await MCMD.download_mod(mainArguments.mod_link, parameters, mainArguments.output)
        
        downloadedIdList.append(dlid)
        
        if dpid:
            dependencyIdList.append(dpid)        
        if not failedStatus:
            successful.append(result)
        else:
            failed.append(result)

    elif mainArguments.ml is not None:
        successful, failed, dependencyIdList, downloadedIdList = await MCMD.multi_download(mainArguments.ml, parameters, mainArguments.output)

    else:
        successful, failed, dependencyIdList, downloadedIdList = await MCMD.txt_download(mainArguments.mltxt, parameters, mainArguments.output)

    resultsPath = os.path.join(mainArguments.output, "results")
    os.makedirs(resultsPath, exist_ok=True)

    if len(successful) > 0:
        successfulPath = os.path.join(resultsPath, 'Successful_downloads.txt')
        successful.sort()
        with open(successfulPath, 'w') as f:
            f.write('- ' + '\n- '.join(successful))


    if len(failed) > 0:
        failedPath = os.path.join(resultsPath, 'Failed_downloads.txt')
        with open(failedPath, 'w') as f:
            f.write('\n'.join(failed))


    async def dependencyHandler(missingDependencies: list[tuple[str, str]]):
        print("Missing Dependencies FOUND")
        print(missingDependencies)
            
            
        txtfile = []
        tasks = []
            
            
        dataTypeTable = { #might not use
            0: ['title', 'name'],
            1: ['', ''] 
        }  
            
            
        async def getName(dep: tuple[str, int]):
            name = await MCUtils.getSpecifiedData(dep, ['title', 'name'])              
            txtfile.append(name)
         
                
        for dep in missingDependencies:
            tasks.append(getName(dep))
                
        await asyncio.gather(*tasks)
                           
        if mainArguments.dd:
                pass #WIP PLACEHOLDER
        else:               
            dependencyPath = os.path.join(resultsPath, 'MissingDependencies.txt')           
            txtfile.sort()
                
            with open(dependencyPath, 'w') as f:
                f.write("- " + "\n- ".join(txtfile))


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
        
        if len(missingDependencies) > 0:
            await dependencyHandler(missingDependencies)


    
def run():
    parser = argparse.ArgumentParser(description="Download minecraft mods from Modrinth and Curseforge automatically (peak laziness)")

    input = parser.add_mutually_exclusive_group(required=True)
    input.add_argument("-m", "--mod-link", help="Single mod download, use a link", metavar="MOD LINK")
    input.add_argument("--ml", "--mod-list", help="Download a bunch of mods simultaneously", metavar="MOD LINKS", nargs="+")
    input.add_argument("--mltxt", "--mod-list-txt", "--dltxt", help="Download the mods from a txt file containing one mod link per line", metavar="TXT FILE")

    parser.add_argument("-g", "--game-version", help="Version of minecraft for the mod (eg: 1.19.2, 1.20.1, etc)")
    parser.add_argument("-l", "--loader", help="The mod loader for this mod (eg: forge, neoforge, fabric)", default=["forge", "neoforge"], nargs='+')
    parser.add_argument("-r", "--restrict", help='Restricts mod to specific version types', choices=["Release", "Beta", "Alpha"], nargs='+')
    parser.add_argument("-d", "--dd", help="Auto downloads any missing dependencies", action="store_true")

    parser.add_argument("-o", "--output", help="Output directory for the mod", default="./")

    try:
        args = parser.parse_args()
        asyncio.run(main(args))
    except SystemExit:
        print("Invalid commands or missing required commands, use --help to see the command list")


if __name__ == "__main__":
    run()