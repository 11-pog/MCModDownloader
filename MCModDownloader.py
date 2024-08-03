from MCSiteAPI import ModrinthAPI
# from MCSiteAPI import CurseforgeAPI WIP
import asyncio

class MCModDownloader:
    def __init__(self):
        self.modrinth_api = ModrinthAPI()
        #self.curseforge_api = CurseforgeAPI() WIP

    async def main():
        api = ModrinthAPI()

        url = 'https://modrinth.com/mod/distanthorizons'

        parameters = {
            'game_versions': ['1.20.1'],
            'loader': ['forge'],
            'version_type': []
        }

        modData = await api.get_project(url)

        version, mod = await api.download(parameters, url=url)    

        with open(f"{modData['slug']}_{version['version_number']}.jar", "wb") as f:
            f.write(mod)

asyncio.run(main())