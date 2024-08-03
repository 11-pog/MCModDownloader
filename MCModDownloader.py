from MCSiteAPI import ModrinthAPI
from MCSiteAPI import CurseforgeAPI
from furl import furl
import os



class MCModDownloader:
    def __init__(self):
        self.modrinth_api = ModrinthAPI()
        self.curseforge_api = CurseforgeAPI()



    async def download_latest(self, url, parameters=None):
        match await self.get_host(url):
            case "modrinth.com":
                MDAPI = self.modrinth_api

                modData = await MDAPI.get_project(url)

                version, mod = await MDAPI.download(parameters, url=url)    

                name = f"{modData['slug']}_{version['version_number']}.jar"  
                return name, mod 
            
            case "www.curseforge.com":
                CFAPI = self.curseforge_api

                modData = await CFAPI.get_project(url)

                version, mod = await CFAPI.download(url, parameters=parameters)

                name = f"{modData['slug']}_{version['displayName'].replace(' ', '-').replace('/', '-')}.jar"
                return name, mod



    async def get_host(self, url):
        f = furl(url)
        host = f.host

        return(host)



    async def saveFile(self, file, name, path):
        try:
            modPath = os.path.join(path, "mods")
            os.makedirs(modPath, exist_ok=True)
            finalPath = os.path.join(modPath, name)
            with open(finalPath, "wb") as f:
                f.write(file)
        except Exception as e:
            print(f"Error saving file: {e}")