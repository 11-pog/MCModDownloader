from MCSiteAPI import ModrinthAPI
# from MCSiteAPI import CurseforgeAPI WIP
import os

class MCModDownloader:
    def __init__(self):
        self.modrinth_api = ModrinthAPI()
        #self.curseforge_api = CurseforgeAPI() WIP

    async def download_latest(self, url, parameters):
        MDAPI = self.modrinth_api

        modData = await MDAPI.get_project(url)

        version, mod = await MDAPI.download(parameters, url=url)    

        name = f"{modData['slug']}_{version['version_number']}.jar"  
        return name, mod 

    async def saveFile(self, file, name, path):
        try:
            fullPath = os.path.join(path, name)
            with open(fullPath, "wb") as f:
                f.write(file)
        except Exception as e:
            print(f"Error saving file: {e}")