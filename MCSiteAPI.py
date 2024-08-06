import aiohttp
import os
import asyncio
from furl import furl

class Http404Error(Exception):
    pass

class HttpError(Exception):
    pass

async def _get(url, *, headers = None, params = None, retries=7):
    for attempt in range(retries):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        return await response.json()
                    else:
                        return await response.text()
                elif response.status != 404:
                    raise HttpError(f"Http get error {response.status}: {response.reason}")
        await asyncio.sleep(0.5)
                
    raise Http404Error()



async def _Dl_Data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = {"Accept": "application/octet-stream"}) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Http get error {response.status}: {response.reason}")



async def _format_query(query):
    formattedQuery = [f'"{x}"' for x in query]
    return ','.join(formattedQuery)


class ModrinthAPI:
    def __init__(self, api_url="https://api.modrinth.com"):
        self.api_url = api_url
        self.utils = utils()
  

    async def get_project(self, url):
        response = await _get(f"{self.api_url}/v2/project/{self.utils.get_slug_by_url(url)}")
        return response



    async def get_project_by_id(self, id, *, retries = 7):
        try:
            response = await _get(f"{self.api_url}/v2/project/{id}", retries=retries)
            return response
        except Http404Error:
            return None
    


    async def get_version(self, version_id):
        response = await _get(f"{self.api_url}/v2/version/{version_id}")
        return response
    


    async def project_files(self, project_slug, parameters = None):
        query = f"{self.api_url}/v2/project/{project_slug}/version"
        
        if parameters:     
            queryParams = []

            version = parameters.get('game_versions')
            if version:
                queryParams.append(f"game_versions=[{await _format_query(version)}]")

            loader = parameters.get('loader')
            if loader:
                queryParams.append(f"loaders=[{await _format_query(loader)}]")
            
            type = parameters.get('version_type')
            if type:
                queryParams.append(f"version_type=[{await _format_query(type)}]")

            query += '?' + '&'.join(queryParams)
            
        fetchResult = await _get(query)
        response = sorted(fetchResult, key=lambda x: x['date_published'], reverse=True)
        return response
    


    async def download(self, url, *,  parameters = None):
        version = None
        if not url:
            raise ValueError("You must provide a valid url")

        project_slug = self.utils.get_slug_by_url(url)
        versionList = await self.project_files(project_slug, parameters)

        if len(versionList) == 0:
            raise ValueError("No mod versions matching game versions or mod loader found, make sure youve gotten the right mod, and/or that it has a version for said loader/game version")

        version = versionList[0]

        fileUrl = version['files'][0]['url']
        response = await _Dl_Data(fileUrl)
        return version, response

    




class CurseforgeAPI:
    def __init__(self, api_url="https://api.curseforge.com"):
        self.api_url = api_url
        api_key = os.environ.get('CF_API_KEY')
        self.utils = utils()

        if api_key is None:
            raise ValueError("CF_API_KEY enviroment variable is not set")
        
        self.api_headers = {
        'Accept': 'application/json',
        'x-api-key': api_key
        }


    async def get_project(self, url):
        mod_id = await self.get_id_by_url(url)
        return await self.get_project_by_id(mod_id)
    


    async def get_project_by_id(self, id, *, retries=7):
        response = await _get(f"{self.api_url}/v1/mods/{id}", headers=self.api_headers, retries=retries)
        return response['data']



    async def get_id_by_url(self, url):
        slug = self.utils.get_slug_by_url(url)  
        return await self.get_id_by_slug(slug)
    


    async def get_id_by_slug(self, slug):
        data = await _get(f'{self.api_url}/v1/mods/search', headers=self.api_headers, params={
            'slug': slug,
            'classId': '6',
            'gameId': '432'
        })

        if len(data['data']) > 0:
            result = data['data'][0]['id']
            return result
        else:
            return None


    async def get_slug_by_url(self, url):
        slug = self.utils.get_slug_by_url(url)
        return slug



    LOADER_MAPPINGS = {
        'forge': '1',
        'cauldron': '2',
        'liteloader': '3',
        'fabric': '4',
        'quilt': '5',
        'neoforge': 6
    }



    async def project_files(self, url, parameters=None):
        finalParamList = []
        id = await self.get_id_by_url(url)
        finalFiles = []

        if parameters:
            params = {}   

            version = parameters.get('game_versions')
            if version:
                params['gameVersion'] = version
            
            loaders = [self.LOADER_MAPPINGS.get(x , 0) for x in parameters.get('loader', [])]
            loaders = set(loaders)

            if len(loaders) > 1:
                for ml in loaders:
                    x = params.copy()
                    x.update({
                        'modLoaderType': ml
                    })

                    finalParamList.append(x)

            else:
                finalParamList = [params.copy()]
                finalParamList[0]['modLoaderType'] = loaders.pop()
                    
            for parameter in finalParamList:
                files = await _get(f'{self.api_url}/v1/mods/{id}/files', headers=self.api_headers, params=parameter)
                finalFiles += files['data']
            
        else:        
            files = await _get(f'{self.api_url}/v1/mods/{id}/files', headers=self.api_headers)
            finalFiles += files['data']

        result = sorted(finalFiles, key=lambda x: x['fileDate'], reverse=True)

        return result
    


    async def download(self, url,  *, parameters = None):
        if not url:
            raise ValueError("You must provide a valid url")

        fileList = await self.project_files(url, parameters)

        if len(fileList) == 0:
            raise ValueError("No mod versions matching game versions or mod loader found, make sure youve gotten the right mod, and/or that it has a version for said loader/game version")

        file = fileList[0]

        fileUrl = file['downloadUrl']
        response = await _Dl_Data(fileUrl)
        return file, response
    

class utils:
    def __init__(self):
        pass
    
    def get_slug_by_url(self, url):
        splitUrl = url.split('/')

        if len(splitUrl) >= 3:
            return splitUrl[-1]
        else:
            raise ValueError("Invalid URL")
