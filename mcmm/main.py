# main.py

import argparse
import asyncio
import configparser
import os

from mcmm.MCModDownloader import MCModDownloader
from mcmm.MCM_Utils import MCM_Utils
from mcmm.MCSiteAPI import ModrinthAPI, CurseforgeAPI

config = configparser.ConfigParser(allow_no_value=True)
configPath = os.path.join(os.path.dirname(__file__), "config")
configFile = os.path.join(configPath, 'config.ini')

if not os.path.exists(configFile):    
    os.makedirs(configPath, exist_ok=True)
    
    config['Curseforge'] = {'api_key': ''}
    with open(configFile, 'w') as f:
        config.write(f)
        
config.read(configFile)

MCMD = MCModDownloader()
MRAPI = ModrinthAPI()
CFAPI = CurseforgeAPI()
MCUtils = MCM_Utils()

async def main(mainArguments):   
    
    successful = []
    failed = []

    downloadedIdList = []
    dependencyIdList = []
    
    parameters = {
        'game_versions': [mainArguments.game_version],
        'loader': mainArguments.loader,
        'version_type': mainArguments.restrict
    }


    if mainArguments.mod_link is not None:
        failedStatus, result, dlid, dpid = await MCMD.download_mod(mainArguments.mod_link, parameters, mainArguments.output)
             
        if dpid:
            dependencyIdList.append(dpid)        
        if not failedStatus:
            downloadedIdList.append(dlid)
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
            
            
        async def getName(dep: tuple[str, int]):
            name = await MCUtils.getSpecifiedData(dep, ['title', 'name'])
            url = await MCUtils.getSpecifiedData(dep, ['slug', ['links', 'websiteUrl']])       
            txtfile.append([name, url])
         
                
        for dep in missingDependencies:
            tasks.append(getName(dep))
                
        await asyncio.gather(*tasks)
                           
        if mainArguments.dd:
                pass #WIP PLACEHOLDER
        else:               
            dependencyPath = os.path.join(resultsPath, 'MissingDependencies.txt')           
            txtfile.sort(key=lambda x: x[0])
            finaltxt = []
            for txt in txtfile:
                finaltxt.append(f"{txt[0]} [{txt[1]}]")
                
            with open(dependencyPath, 'w') as f:
                f.write("- " + "\n- ".join(finaltxt))


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
    input.add_argument("-c", "--config", help="configurations for the lib", nargs='*')

    parser.add_argument("-g", "--game-version", help="Version of minecraft for the mod (eg: 1.19.2, 1.20.1, etc)")
    parser.add_argument("-l", "--loader", help="The mod loader for this mod (eg: forge, neoforge, fabric)", default=["forge", "neoforge"], nargs='+')
    parser.add_argument("-r", "--restrict", help='Restricts mod to specific version types', choices=["Release", "Beta", "Alpha"], nargs='+')
    parser.add_argument("-d", "--dd", help="Auto downloads the missing dependencies [WIP]", action="store_true")

    parser.add_argument("-o", "--output", help="Output directory for the mod", default="./")
    
    
    
    try:
        args = parser.parse_args()
        
        if args.dd:
            print('Sorry but auto downloading dependencies is still WIP')
        
        if args.config is not None:
            if len(args.config) == 0 or args.config[0] != 'cf-api-key':
                print(
                    "Configuration list\n"
                    "CURSEFORGE:\n"
                    '  "cf-api-key [key]" -> sets the curseforge api key\n'
                    'thats it for now lmao'
                )
                return
                
            if len(args.config) < 2:
                print('Please enter a valid key')
                return
                
            config.set('Curseforge', 'api_key', args.config[1])
                
            with open(configFile, 'w') as file:                
                config.write(file)
            
            CFAPIInstance = CurseforgeAPI()             
            if not asyncio.run(CFAPIInstance.is_key_valid()):
                print("Invalid api key")
                return
            
            print(
                "Api key set\n"
                "You can now use the mcmm package"
                )
            return
        
    
        if config['Curseforge']['api_key'] == '':
            print(
                "You do not have a Curseforge API KEY setup\n"
                "Please run \"mcmm -c cf-api-key [your api key]\" to define a API key\n"
                "If you do not have a API key, go to 'https://console.curseforge.com/#/api-keys' to get one"
                )
            return
          
        if not asyncio.run(CFAPI.is_key_valid()):
            print(
                "Invalid CurseForge api key\n"
                "Please run \"mcmm -c cf-api-key [your api key]\" to define a API key\n"
                "If you do not have a API key, go to 'https://console.curseforge.com/#/api-keys' to get one"
                )
            return
        
        asyncio.run(main(args))
    except SystemExit:
        print("Invalid commands or missing required commands, use --help to see the command list")


if __name__ == "__main__":
    run()