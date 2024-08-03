import aiohttp
import asyncio
import os
from furl import furl

async def _get(url, *, headers = None, params = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return await response.json()
                else:
                    return await response.text()
            else:
                raise Exception(f"Http get error {response.status}: {response.reason}")
            
async def _Dl_Data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = {"Accept": "application/octet-stream"}) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Http get error {response.status}: {response.reason}")
            
def _formatParams(params):
    return ",".join(f'"{value}"' for value in params)

def _splitUrl(url, separator):
        splitUrl = url.split(separator)

        if len(splitUrl) == 2:
            return splitUrl[1]
        else:
            raise ValueError("Invalid URL")
        
class ModrinthAPI:
    def __init__(self, api_url="https://api.modrinth.com"):
        self.api_url = api_url


    
    async def get_project(self, url):
        response = await _get(f"{self.api_url}/v2/project/{_splitUrl(url, '/mod/')}")
        return response



    async def get_version(self, version_id):
        response = await _get(f"{self.api_url}/v2/version/{version_id}")
        return response
    


    async def project_files(self, project_slug, parameters):
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

        fetchResult = await _get(query)
        response = sorted(fetchResult, key=lambda x: x['date_published'], reverse=True)
        return response
    


    async def download(self, parameters = None,  *, version_id = None, url = None):
        version = None
        if not (version_id or (parameters and url)):
            raise ValueError("You must provide either version_id or both the parameters and url")

        if version_id:
            version = await ModrinthAPI.get_version(self, version_id)
        else:
            project_slug = _splitUrl(url, '/mod/')
            versionList = await ModrinthAPI.project_files(self, project_slug, parameters)
            version = versionList[0]

        fileUrl = version['files'][0]['url']
        response = await _Dl_Data(fileUrl)
        return version, response

    

class CurseforgeAPI:
    def __init__(self, api_url="https://api.curseforge.com"):
        self.api_url = api_url
        api_key = os.environ.get('CF_API_KEY')

        if api_key is None:
            raise ValueError("CF_API_KEY enviroment variable is not set")
        
        self.api_headers = {
        'Accept': 'application/json',
        'x-api-key': api_key
        }

    async def get_id_by_slug(self, url):
        slug = _splitUrl(url, '/mc-mods/')
        data = await _get(f'{self.api_url}/v1/mods/search', headers=self.api_headers, params={
            'slug': slug,
            'classId': '6',
            'gameId': '432'
        })

        result = data['data'][0]['id']

        return result
    
    async def project_files(self, url, parameters=None):

        if parameters:
            CFParams = {


                
            }


        id = await self.get_id_by_slug(url)
        files = await _get(f'{self.api_url}/v1/mods/{id}/files', headers=self.api_headers)

        result = sorted(files['data'], key=lambda x: x['fileDate'], reverse=True)

        print(result)
       
CFAPI = CurseforgeAPI()
print(asyncio.run(CFAPI.project_files('https://www.curseforge.com/minecraft/mc-mods/mouse-tweaks')))