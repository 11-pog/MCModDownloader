import aiohttp

async def _fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return await response.json()
                else:
                    return await response.text()
            else:
                return None
            
async def _Dl_Data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = {"Accept": "application/octet-stream"}) as response:
            if response.status == 200:
                return await response.read()
            else:
                return None
            
def _formatParams(params):
    return ",".join(f'"{value}"' for value in params)

def _splitUrl(url):
        splitUrl = url.split('/mod/')

        if len(splitUrl) == 2:
            return splitUrl[1]
        else:
            raise ValueError("Invalid URL")
        
class ModrinthAPI:
    def __init__(self, api_url="https://api.modrinth.com"):
        self.api_url = api_url

    
    async def get_project(self, url):
        response = await _fetch_data(f"{self.api_url}/v2/project/{_splitUrl(url=url)}")
        return response

    async def get_version(self, version_id):
        response = await _fetch_data(f"{self.api_url}/v2/version/{version_id}")
        return response
    
    async def project_versions(self, project_slug, parameters):
        query = f"{self.api_url}/v2/project/{project_slug}/version"
        if parameters:
            version = parameters['game_versions']
            loader = parameters['loader']
            type = parameters['version_type']

            queryParams = []

            if version:
                queryParams.append(f"game_versions=[{_formatParams(version)}]")
            if loader:
                queryParams.append(f"loaders=[{_formatParams(loader)}]")
            if type:
                queryParams.append(f"version_type=[{_formatParams(type)}]")
            
            if queryParams:
                query += "?" + "&".join(queryParams)

        fetchResult = await _fetch_data(query)
        response = sorted(fetchResult, key=lambda x: x['date_published'], reverse=True)
        return response
    
    async def download(self, parameters = None,  *, version_id = None, url = None):
        version = None
        if not (version_id or (parameters and url)):
            raise ValueError("You must provide either version_id or both the parameters and url")

        if version_id:
            version = await ModrinthAPI.get_version(self, version_id)
        else:
            project_slug = _splitUrl(url=url)
            versionList = await ModrinthAPI.project_versions(self, project_slug, parameters)
            version = versionList[0]

        fileUrl = version['files'][0]['url']
        response = await _Dl_Data(fileUrl)
        return version, response

    
class CurseforgeAPI:
    def __init__(self, api_url="https://api.curseforge.com"):
        self.api_url = api_url

    #work in progress