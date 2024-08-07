# MCModDownloader.py

from mcmm.MCSiteAPI import ModrinthAPI, CurseforgeAPI, utils
from mcmm.MCM_Utils import MCM_Utils
from typing import Literal
import os


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



    async def saveFile(self, file: bytes, name: str, path: str):
        try:
            modPath = os.path.join(path, "mods")
            os.makedirs(modPath, exist_ok=True)
            finalPath = os.path.join(modPath, name)
            with open(finalPath, "wb") as f:
                f.write(file)
        except Exception as e:
            print(f"Error saving file: {e}")