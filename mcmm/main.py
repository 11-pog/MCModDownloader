# main.py


# General Imports
import argparse
import asyncio
import subprocess
import os
import sys


# Imports custom classes
from mcmm.MCModDownloader import MCModDownloader
from mcmm.MCM_Utils import MCM_Utils
from mcmm.MCSiteAPI import ModrinthAPI, CurseforgeAPI
from helpers import cache, config, general


# TODO: Use a form of cache to store info about downloaded mods so that there is no need to make rpeated API calls on the dependency checking part (besides just being generally faster)
mod_data_cache = []

configPath = os.path.join(os.path.dirname(__file__), "config") # Configs dir path

configFile = os.path.join(configPath, 'config.ini') # Config.ini path
cacheFile = os.path.join(configPath, 'MCMM_Cache.json') # MCMM_Cache.json path

app_config = config(configFile)
app_cache = cache(cacheFile)
_general = general()

def deconstruct_mlconfig() -> list:
    return app_config['General'].get('default_mod_loader').split(' ')

def open_file_and_wait(path: str):
    """Generic open txt file and wait until its closed function. Uses notepad.

    Args:
        path (str): Path to the file to be opened
    """
    if os.name == 'nt':
        subprocess.Popen(['notepad.exe', path]).communicate()
        
    elif os.name == 'posix':
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.Popen([opener, path]).communicate()


# Creating Class instances
MCMD = MCModDownloader()
MRAPI = ModrinthAPI()
CFAPI = CurseforgeAPI()
MCUtils = MCM_Utils()


async def main(mainArguments: argparse.Namespace) -> None:
    """Main entry point

    Args:
        mainArguments (argparse.Namespace): Parsed arguments
    """
    app_cache.clearCache()
    
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
        with open(successfulPath, 'w', encoding='utf-8') as f:
            f.write('- ' + '\n- '.join(successful))


    if len(failed) > 0:
        failedPath = os.path.join(resultsPath, 'Failed_downloads.txt')
        with open(failedPath, 'w', encoding='utf-8') as f:
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
        
        prioritize_cf = app_config['Other']['prioritize_cf'] == 'True'
                        
        async def getName(dep: tuple[str, int]):
            name = await MCUtils.getSpecifiedData(dep, ['title', 'name'], prioritizeCF=prioritize_cf)
            url, hostid = await MCUtils.getSpecifiedData(dep, ['slug', ['links', 'websiteUrl']], prioritizeCF=prioritize_cf)       
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
                
        with open(dependencyPath, 'w', encoding='utf-8') as f:
            f.write("- " + "\n- ".join(finaltxt))
            
        absDependencyPath = os.path.abspath(dependencyPath)
        app_cache('DEPENDENCY_PATH', absDependencyPath)


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
        dependencyPath = app_cache('DEPENDENCY_PATH')
        
        if dependencyPath is None:
            print("There are no cached dependencies to be resolved")
            return
                        
        print("Opening file, close the file to continue...")
        open_file_and_wait(dependencyPath)                  
        print('Done!')



def get_arguments() -> tuple[argparse.Namespace, int]:
    parser = argparse.ArgumentParser(description="Download minecraft mods from Modrinth and Curseforge automatically (peak laziness)")  
    defaultOutput = app_config["General"]['default_output_dir']
    
    input = parser.add_mutually_exclusive_group()
        
    input.add_argument("-m", "--mod-link", help="Single mod download, use a link", metavar="MOD LINK")
    input.add_argument("-ml", "--mod-list", help="Download a bunch of mods simultaneously", metavar="MOD LINKS", nargs="+")
    input.add_argument("-mlt", "--mod-list-txt", "-dlt", help="Download the mods from a txt file containing one mod link per line", metavar="TXT FILE")
        
    # Mod fetching parameters
    mod_group = parser.add_argument_group(title="Mod filtering parameters", description="Parameters to help fetch specific mod versions")
    mod_group.add_argument("-g", "--game-version", help="Version of minecraft for the mod (eg: 1.19.2, 1.20.1, etc)")
    mod_group.add_argument("-l", "--loader", help=f"The mod loader for this mod (eg: forge, neoforge, fabric) (default = {', '.join(deconstruct_mlconfig())})", default=deconstruct_mlconfig(), nargs='+')
    mod_group.add_argument("-r", "--restrict", help="Restricts mod to specific version types [DEPRECATED: Broken]", choices=["Release", "Beta", "Alpha"], nargs='+') # DEPRECATED: Broken
    
    # Extra parameters
    extra_group = parser.add_argument_group(title="Extra commands", description="Extra commands for this package")
    extra_group.add_argument("-o", "--output", help=f"Output directory for the mod, current default = '{defaultOutput}'. use -c default-output-dir to set or change this", default=defaultOutput)
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
        key = _general.get_element(args.config, 0)
        value = _general.get_element(args.config, 1)
        other = _general.get_element(args.config, 2, tillEnd=True)
        
        try:
            configure(key, value, other)
        except ValueError:
            sys.exit(0)
        
    
    if app_config['Curseforge']['api_key'] == '':
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



def configure(key: str|None, value: str|int|None, other: list):
    def check_value():
        if value is None:
            print(f'Please enter a valid value for {key}')
            raise ValueError()
            
    match key:
        case "cf-api-key":
            check_value()    
                           
            app_config.setConfig('Curseforge', 'api_key', value)
                    
            CFAPIInstance = CurseforgeAPI()             
            if not asyncio.run(CFAPIInstance.is_key_valid()):
                print("Invalid api key")
                return
                    
            print(
                "Api key set\n"
                "You can now use the mcmm package"
                )      
            
                  
        case 'default-mod-loader':
            check_value()
            
            loaders = [value] + other if other else [value]
            
            def getModLoader(input):
                match input.lower():
                    case 'fabric':
                        return 'fabric'
                        
                    case 'forge':
                        return 'forge'
                    
                    case 'neoforge':
                        return 'neoforge'
                    
                    case 'quilt':
                        return 'quilt'
                    
                    case _:
                        print(f"Invalid mod loader: {input}")
                        raise ValueError

            MlList = []
                    
            for ml in loaders:
                MlList.append(getModLoader(ml))
                        
            app_config.setConfig('General', 'default_mod_loader', ' '.join(MlList))
                 
        
        case 'default-output-dir':
            check_value()
            
            match value:               
                case 'cwd':
                    app_config.setConfig('General', 'default_output_dir', './')
                    print(f"The default output is now set to the current working directory at runtime")
                case './':
                    cwd = os.getcwd()
                    app_config.setConfig('General', 'default_output_dir', cwd)
                    print(f"The default output directory is now set to this directory: {cwd}")
                case str():
                    if os.path.exists(value):
                        absvalue = os.path.abspath(value)
                        app_config.setConfig('General', 'default_output_dir', absvalue)
                        print(f"The default output is now set to {absvalue}")
                    else:
                        print(f"Invalid path: {value}")
                        raise ValueError()
        
        
        case 'prioritize-cf':
            match value:
                case 'true'|'True':
                    app_config.setConfig('Other', 'prioritize_cf', 'True')
                    print('The dependencies will now prioritize Curseforge')
                case 'false'|'False':
                    app_config.setConfig('Other', 'prioritize_cf', 'False')
                    print('The dependencies will now prioritize Modrinth')
                case _:
                    switchedValue = 'False' if app_config['Other']['prioritize_cf'] == 'True' else 'True'
                    app_config.setConfig('Other', 'prioritize_cf', switchedValue)
                    print(f'prioritize-cf now toggled to {switchedValue}')
                    
                
        case _:
            defaultOutput = app_config['General'].get('default_output_dir')
            print(f"""
Configuration list:
    Curseforge:
            "cf-api-key [key]" -> sets the curseforge api key
            
    General:
            "default-output-dir [path]" = '{'cwd' if defaultOutput == './' else defaultOutput}' -> the default output directory for downloads.
                                ^^^^^^ Can be either an valid path, './', or 'cwd'
                                "cwd" sets the default output directory to the current working directory of the script at runtime, which means it will change depending on the directory from which the script is run. For example, if you run the script in D:/Videos, the default output directory will be D:/Videos, and if you run it in C:/Images, the default output directory will be C:/Images.
                                "./" sets the default output directory to the absolute path of the current working directory at the time the setting is configured, which means it will remain fixed even if the script is run from a different directory. For example, if you set defaultoutputdir ./ while running the script in C:/Images, the default output directory will always be C:/Images, even if you run the script in D:/Videos later.
                                
            "default-mod-loader [loader_name] [additional_loaders]" = '{', '.join(deconstruct_mlconfig())}' -> sets the default mod loader.
                                Available mod loaders: fabric, forge, neoforge, and quilt
                                Example: "default-mod-loader forge neoforge"                 
                                
    Dependencies:
            "prioritize-cf [True or False]" = {app_config['Other']['prioritize_cf']} -> as of now, anything dependency related autos to modrinth as default, set this to true to change this behavior to curseforge
                        Toggles in case the value is not provided (or is invalid)
                        
    thats it for now lmao               
                """)
    sys.exit(0)
    
   
""" 
CONFIGURATION CONCEPTS FOR THE FUTURE MAYBE MAYBE:
    Dependency resolution
    - api-priority [modrinth, curseforge] -> as of now, anything dependency related autos to modrinth default (to curseforge only if it is not on modrinth), this could help set the priority for the user
    ^ as for now imma implement it as a bool called prioritize-cf, which accepts true, false or none (case none it toggles)
    
    Debug?
    - maybe verbose level?? i just dont know what i would change in questions of printing
    
"""



if __name__ == "__main__":
    run()