# MCM_Utils.py

from typing import Literal
from furl import furl

from mcmm.MCSiteAPI import ModrinthAPI, CurseforgeAPI

class MCM_Utils:
    def __init__(self):
        self.modrinth_api = ModrinthAPI()
        self.curseforge_api = CurseforgeAPI()



    async def get_equivalent_ids(self, id: dict) -> tuple[str, int]:
        CFId = MDId = None
        
        if id.get('modId') is not None:
            CFId = id['modId']
            project = await self.curseforge_api.get_project_by_id(CFId)
            if project.get('slug'):
                mdProject = await self.modrinth_api.get_project_by_id(project['slug'])
                if mdProject is not None:
                    MDId = mdProject['id']
        else:
            MDId = id['project_id']
            project = await self.modrinth_api.get_project_by_id(MDId)
            if project.get('slug'):
                CFId = await self.curseforge_api.get_id_by_slug(project['slug'])
                
        """
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
        """
                        
        print(f"Equivalent ID's: {MDId}, {CFId}")
        return MDId, CFId
    
    
    async def getSpecifiedData(self, dep: tuple[str, str], dataTypes: tuple[str, str], *, prioritizeCF: bool = False) -> tuple[str | dict | list, int]:
        async def getData(api: object, path: str | list, id: str):
            project = await api.get_project_by_id(id, retries=20)
            
            if isinstance(path, list):
                value = project
                for key in path:
                    value = value[key]
                return value
            
            return project[path]
                
        data = None
        hostid = 0
        
        if prioritizeCF and dep[1] is not None:
            data = await getData(self.curseforge_api, dataTypes[1], dep[1])
            hostid = 1
        elif dep[0] is not None:
            data = await getData(self.modrinth_api, dataTypes[0], dep[0])
        else:
            data = await getData(self.curseforge_api, dataTypes[1], dep[1])
            hostid = 1
            
        return data, hostid
    
    
    
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
    
    

        