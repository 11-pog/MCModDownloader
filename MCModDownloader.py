import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return await response.json()
                else:
                    return await response.text()
            else:
                return None
            
async def Dl_Data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = {"Accept": "application/octet-stream"}) as response:
            if response.status == 200:
                return await response.read()
            else:
                return None
            
def formatParams(params):
    return ",".join(f'"{value}"' for value in params)

class ModrinthAPI:
    def __init__(self, api_url="https://api.modrinth.com"):
        self.api_url = api_url

    async def get_project(self, project_slug):
        response = await fetch_data(f"{self.api_url}/v2/project/{project_slug}")
        return response

    async def get_version(self, version_id):
        response = await fetch_data(f"{self.api_url}/v2/version/{version_id}")
        return response
    
    async def project_versions(self, project_slug, parameters):
        query = f"{self.api_url}/v2/project/{project_slug}/version"
        if parameters:
            version = parameters['game_versions']
            loader = parameters['loader']

            query_params = []
            
            if version:
                query_params.append(f"game_versions=[{formatParams(version)}]")
            if loader:
                query_params.append(f"loaders=[{formatParams(loader)}]")
            
            if query_params:
                query += "?" + "&".join(query_params)

        response = await fetch_data(query)
        return response

    async def download(self, version_id):
        file_version = await ModrinthAPI.get_version(self, version_id)
        file_url = file_version['files'][0]['url']
        print(file_url)
        response = await Dl_Data(file_url)
        return file_version, response
    
class CurseforgeAPI:
    def __init__(self, api_url="https://api.curseforge.com"):
        self.api_url = api_url