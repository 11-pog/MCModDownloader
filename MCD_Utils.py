from MCSiteAPI import ModrinthAPI
from MCSiteAPI import CurseforgeAPI
from MCModDownloader import MCModDownloader

class utils:
    def __init__(self):
        self.cfapi = CurseforgeAPI()
        self.mrapi = ModrinthAPI()

    async def getCounterpart(self, id, host):
        match host:
            case "modrinth.com":
                pass
            case "www.curseforge.com":
                pass
