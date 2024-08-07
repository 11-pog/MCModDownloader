# MCModDownloader.py

from MCSiteAPI import ModrinthAPI, CurseforgeAPI, utils
from MCM_Utils import MCM_Utils
from typing import Literal
import os
import asyncio


class MCModDownloader:
    def __init__(self):
        self.modrinth_api = ModrinthAPI()
        self.curseforge_api = CurseforgeAPI()
        self.utils = MCM_Utils()



    async def download_latest(self, url: str, parameters: dict=None) -> tuple[str, bytes, dict, Literal['modrinth.com', 'www.curseforge.com']]:

        host = await self.utils.get_host(url)
        filename = metadata = files = None
        
        async def getModData(API: object):
            modData = await API.get_project(url)
            metadata, files = await API.download(url, parameters=parameters)

            return modData, metadata, files

        match host:
            case "modrinth.com":
                modData, metadata, files = await getModData(self.modrinth_api)
                filename = f"{modData['slug']}_{metadata['version_number']}.jar"  
            
            case "www.curseforge.com":
                modData, metadata, files = await getModData(self.curseforge_api)
                filename = f"{modData['slug']}_{metadata['id']}.jar"

        return filename, files, metadata, host


    
    async def download_mod(self, url: str, params: dict[str, str], output: str) -> tuple[bool, str, str, str|None]:
        
        result = downloadedId = dependencyId = None
        failedStatus = False   
        
        try:
            result, mod, metadata, host = await self.download_latest(url, params)
            await self.saveFile(mod, result, output)
            print(f"sucessfully downloaded {result}")
            
            downloadedId = (
                {'data': metadata['modId'], 'host': host}
                if host == "www.curseforge.com" else
                {'data': metadata['project_id'], 'host': host}
                )
            
            if len(metadata['dependencies']) > 0:
                dependencyId = {'data': metadata['dependencies'], 'host': host}
            

        except Exception as e:
            print(f"Error downloading {url}: {e}")
            result = (f"Failed to Download: {url}\nCause: {e}")
            failedStatus = True
            
        return failedStatus, result, downloadedId, dependencyId



    async def multi_download(self, linklist: list[str], params: dict[str, str], output: str) -> tuple[list[str], list[str], list[str], list[str]]:
        task = []
        
        successfulList = []
        failedList = []
                
        dependencyList = []
        downloadedList = []
                
        async def _simultaneousDownloads(url, params: dict[str, str], output: str):
            failedStatus, result, dlid, dpid = await self.download_mod(url, params, output)
            downloadedList.append(dlid)
            
            if dpid:
                dependencyList.append(dpid)
            
            if not failedStatus:
                successfulList.append(result)
            else:
                failedList.append(result)
        
        for link in linklist:
            task.append(_simultaneousDownloads(link, params, output))   
                                                        
        await asyncio.gather(*task)
        
        return successfulList, failedList, dependencyList, downloadedList



    async def txt_download(self, txtfile: str, params: dict[str, str], output: str) -> tuple[list[str], list[str], list[str], list[str]]:
        try:
            with open(txtfile, 'r') as file:      
                linklist = []
                for line in file:
                    link = line.strip()
                    if link:
                        linklist.append(link)
                        
                return await self.multi_download(linklist, params, output)
                        
        except FileNotFoundError:
            print(f"ERROR: Input file {txtfile} was not found")
        except ValueError as e:
            print(f"An error occurred: {e}")
            
        return [], [], [], []
    
    

    async def saveFile(self, file: bytes, name: str, path: str):
        try:
            modPath = os.path.join(path, "mods")
            os.makedirs(modPath, exist_ok=True)
            finalPath = os.path.join(modPath, name)
            with open(finalPath, "wb") as f:
                f.write(file)
        except Exception as e:
            print(f"Error saving file: {e}")