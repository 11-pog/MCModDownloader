# MCM_Utils

from mcmm.MCSiteAPI import ModrinthAPI, CurseforgeAPI
from typing import Literal
from furl import furl


class MCM_Utils:
    def __init__(self):
        self.modrinth_api = ModrinthAPI()
        self.curseforge_api = CurseforgeAPI()



    async def get_equivalent_ids(self, id: str | int, host: Literal['modrinth.com', 'www.curseforge.com']) -> tuple[str, int]:
        CFId = MDId = None

        match host:
            case "modrinth.com":   
                MDId = id['project_id']
                project = await self.modrinth_api.get_project_by_id(MDId)
                if project.get('slug'):
                    CFId = await self.curseforge_api.get_id_by_slug(project['slug'])
            case "www.curseforge.com":
                CFId = id['modId']
                project = await self.curseforge_api.get_project_by_id(CFId)
                if project.get('slug'):
                    mdProject = await self.modrinth_api.get_project_by_id(project['slug'])
                    if mdProject is not None:
                        MDId = mdProject['id']
        print(f"Equivalent ID's: {MDId}, {CFId}")
        return [MDId, CFId]
    
    
    
    async def getSpecifiedData(self, dep: tuple[str, str], dataTypes: tuple[str, str], *, prioritizeCF: bool = False) -> str | dict | list:
        async def getData(api: object, name: str, id: str):
            project = await api.get_project_by_id(id, retries=20)
            return project[name]
                
        data = None
        if prioritizeCF and dep[1] is not None:
            data = await getData(self.curseforge_api, dataTypes[1], dep[1])
        elif dep[0] is not None:
            data = await getData(self.modrinth_api, dataTypes[0], dep[0])
        else:
            data = await getData(self.curseforge_api, dataTypes[1], dep[1])
            
        return data
    
    
    
    async def returnModName(self, data: any, host: Literal['modrinth.com', 'www.curseforge.com']) -> str:
        async def getModName(API: object, id: str | int) -> dict:
            project = await API.get_project_by_id(id)
            return project

        match host:
            case "modrinth.com":
                id = data[0]['project_id']
                metadata = await getModName(self.modrinth_api, id)
                return metadata['title']
            case "www.curseforge.com":
                id = data[0]['modId']
                metadata = await getModName(self.curseforge_api, id)
                return metadata['name']
    
    
    
    async def get_host(self, url: str) -> str:
        f = furl(url)
        host = f.host

        return(host)  