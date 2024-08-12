# main.py

import argparse
import asyncio
import configparser
import subprocess
import os
import sys
import json

from mcmm.MCModDownloader import MCModDownloader
from mcmm.MCM_Utils import MCM_Utils
from mcmm.MCSiteAPI import ModrinthAPI, CurseforgeAPI

config = configparser.ConfigParser(allow_no_value=True)
configPath = os.path.join(os.path.dirname(__file__), "config")
configFile = os.path.join(configPath, 'config.ini')
cacheFile = os.path.join(configPath, 'MCMM_Cache.json')

def cache(key:str, value:any=None) -> dict|None:
    """Simple cache function, caches the data in value to the specified key, return the key data if key is None.

    Args:
        key (str): the specified json key.
        value (any, optional): Value to write to the key. Returns the key value if None. Defaults to None.

    Returns:
        dict|None: The value of the specified key, None if writing.
    """
    
    if value is None:        
        with open(cacheFile, 'r') as f:
            data = json.load(f)
            return data.get(key)
        
    with open(cacheFile, 'r+') as f:
            data = json.load(f)
            data[key] = value
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
def saveConfig():
    """Saves the current loaded config into the config.ini file.
    """
    with open(configFile, 'w') as f:
        config.write(f)

def open_file_and_wait(path: str):
    """Generic open txt file and wait until its closed function.
    Uses notepad.

    Args:
        path (str): Path to the file to be opened
    """
    if os.name == 'nt':
        subprocess.Popen(['notepad.exe', path]).communicate()
        
    elif os.name == 'posix':
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.Popen([opener, path]).communicate()

os.makedirs(configPath, exist_ok=True)

if not os.path.exists(configFile):
    saveConfig()
    
if not os.path.exists(cacheFile):
    with open(cacheFile, 'w') as f:
        json.dump({}, f)

config.read(configFile)

if not config.has_section('Curseforge'):
    config.add_section('Curseforge')

config['Curseforge'].setdefault('api_key', '')

saveConfig()

MCMD = MCModDownloader()
MRAPI = ModrinthAPI()
CFAPI = CurseforgeAPI()
MCUtils = MCM_Utils()


async def main(mainArguments: argparse.Namespace) -> None:
    """Main entry point

    Args:
        mainArguments (argparse.Namespace): Parsed arguments
    """
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

    elif mainArguments.mod_list is not None:
        successful, failed, dependencyIdList, downloadedIdList = await MCMD.multi_download(mainArguments.mod_list, parameters, mainArguments.output)

    else:
        successful, failed, dependencyIdList, downloadedIdList = await MCMD.txt_download(mainArguments.mod_list_txt, parameters, mainArguments.output)

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


    async def dependencyHandler(missingDependencies: list[tuple[str, str]]) -> None:
        print("""
Missing Dependencies FOUND
MissingDependencies.txt created

Run mcmm -rw to open the file and edit it if necessary.
Make sure to check the detected missing dependencies before trying to resolve. [WIP]
""")
            
        txtfile = []
        tasks = []
                        
        async def getName(dep: tuple[str, int]):
            name = await MCUtils.getSpecifiedData(dep, ['title', 'name'])
            url, hostid = await MCUtils.getSpecifiedData(dep, ['slug', ['links', 'websiteUrl']])       
            txtfile.append((name, (url, hostid)))
         
                
        for dep in missingDependencies:
            tasks.append(getName(dep))
                
        await asyncio.gather(*tasks)
                                        
        dependencyPath = os.path.join(resultsPath, 'MissingDependencies.txt')           
        txtfile.sort(key=lambda x: x[0])
        finaltxt = []
        
        for txt in txtfile:
            url = txt[1][0] if txt[1][1] == 1 else f"https://modrinth.com/mod/{txt[1][0]}"
            finaltxt.append(f"{txt[0][0 ]} [{url}]")
                
        with open(dependencyPath, 'w') as f:
            f.write("- " + "\n- ".join(finaltxt))
            
        absDependencyPath = os.path.abspath(dependencyPath)
        cache('DEPENDENCY_PATH', absDependencyPath)


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

        async def dependencyAppendId(data):
            ids = await MCUtils.get_equivalent_ids(data)
            equivalentDependencyIds.append(ids)

        tasks = []
        for data, _ in requiredDependencies:
            tasks.append(dependencyAppendId(data))
        
        await asyncio.gather(*tasks)

        missingDependencies = [
            dependency for dependency in equivalentDependencyIds
            if not any(value in [id['data'] for id in downloadedIdList] for value in dependency)
        ]
        
        if len(missingDependencies) > 0:
            await dependencyHandler(missingDependencies)



def dependencyResolve(args): #WIP
    if args.review == True:
        dependencyPath = cache('DEPENDENCY_PATH')
        
        if dependencyPath is not None:
            print("Opening file, close the file to continue...")
            open_file_and_wait(dependencyPath)
        else:
            print("There are no cached dependencies to be resolved")
            
        print('Done!')
        return



def get_arguments() -> tuple[argparse.Namespace, int]:
    parser = argparse.ArgumentParser(description="Download minecraft mods from Modrinth and Curseforge automatically (peak laziness)")  
    
    input = parser.add_mutually_exclusive_group()
        
    input.add_argument("-m", "--mod-link", help="Single mod download, use a link", metavar="MOD LINK")
    input.add_argument("-ml", "--mod-list", help="Download a bunch of mods simultaneously", metavar="MOD LINKS", nargs="+")
    input.add_argument("-mlt", "--mod-list-txt", "-dlt", help="Download the mods from a txt file containing one mod link per line", metavar="TXT FILE")
        
    # Mod fetching parameters
    mod_group = parser.add_argument_group(title="Mod filtering parameters", description="Parameters to help fetch specific mod versions")
    mod_group.add_argument("-g", "--game-version", help="Version of minecraft for the mod (eg: 1.19.2, 1.20.1, etc)")
    mod_group.add_argument("-l", "--loader", help="The mod loader for this mod (eg: forge, neoforge, fabric)", default=["forge", "neoforge"], nargs='+')
    mod_group.add_argument("-r", "--restrict", help="Restricts mod to specific version types [DEPRECATED: Broken]", choices=["Release", "Beta", "Alpha"], nargs='+') # DEPRECATED: Broken
    
    # Extra parameters
    extra_group = parser.add_argument_group(title="Extra commands", description="Extra commands for this package")
    extra_group.add_argument("-o", "--output", help="Output directory for the mod", default="./")
    extra_group.add_argument("-c", "--config", help="configurations for this package", nargs='*')
    
    # WIP: Dependency resolution commands - Currently dont do anything     
    dep_group = parser.add_argument_group(title="Dependency resolution", description="WIP: Commands to help manage and resolve missing dependencies")   
     
    dep_group.add_argument("-rd", "--resolve",
                           help="Not implemented: Attempts to resolve any cached missing dependencies. Before using this command, it's recommended to run `--review` to verify the dependencies, as some mods may report false positives.",
                           action="store_true")
    
    dep_group.add_argument("-bl", "--blacklist",
                           help="Not implemented: Automatically blacklists any removed dependencies, preventing them from being detected in the future. Use this option to ignore dependencies that are no longer required or are causing issues.",
                           action="store_true")
    
    dep_group.add_argument("-rw", "--review",
                           help="Opens the missing dependencies file for manual review and editing. This allows you to verify and correct any dependencies before attempting to resolve them.",
                           action="store_true")
    
    try:
        args = parser.parse_args()
        
        isDependency = args.resolve or args.blacklist or args.review
        isDownload = args.mod_link or args.mod_list or args.mod_list_txt
        isConfig = args.config is not None
        
        if not(isDependency or isDownload or isConfig):
            print("Error: You must pass arguments. Try `--help` for usage instructions.")
            raise SystemExit(0)
        
        return args, 0 if isDownload else 1 if isDependency else 2
    except SystemExit as e:
        if e.code == 2:
            print("Error: Invalid arguments. Try `--help` for usage instructions.")
                        
        sys.exit(e.code)

    
    
def run():        
    args, call_type = get_arguments()
        
    if call_type == 1:
        dependencyResolve(args)
        return
    
    if call_type == 2:
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
        saveConfig()
            
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
"""
    You do not have a Curseforge API KEY setup!
            
    Please run \"mcmm -c cf-api-key [your api key]\" to define a API key.
    If you do not have a API key, go to 'https://console.curseforge.com/#/api-keys' to get one.
"""            
            )
        return
          
    if not asyncio.run(CFAPI.is_key_valid()):
        print(
""" 
    Invalid CurseForge api key!
            
    Please run \"mcmm -c cf-api-key [your api key]\" to define a API key.
    If you do not have a API key, go to 'https://console.curseforge.com/#/api-keys' to get one.
"""
            )
        return
        
    asyncio.run(main(args))



if __name__ == "__main__":
    run()