import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
            
async def Dl_Data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = {"Accept": "application/octet-stream"}) as response:
            if response.status == 200:
                return await response.read()
            else:
                return None

class ModrinthAPI:
    def __init__(self, api_url="https://api.modrinth.com"):
        self.api_url = api_url

    async def get_project(self, project_id):
        response = await ModrinthAPI.fetch_data(f"{self.api_url}/v2/project/{project_id}")
        return response

    async def get_project_by_link(self, url):
        response = await ModrinthAPI.fetch_data(url)
        return response

    async def get_version(self, version_id):
        response = await ModrinthAPI.fetch_data(f"{self.api_url}/v2/version/{version_id}")
        return response

    async def download_mod(self, version_id):
        file_version = await ModrinthAPI.get_version(self, version_id)
        file_url = file_version['files'][0]['url']
        print(file_url)
        response = await ModrinthAPI.Dl_Data(file_url)
        return file_version, response
    
class CurseforgeAPI:
    def __init__(self, api_url="https://api.curseforge.com"):
        self.api_url = api_url