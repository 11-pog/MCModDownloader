# MCSiteAPI.py

import aiohttp
import os
import asyncio
import configparser

class Http404Error(Exception):
    pass

class HttpError(Exception):
    pass

class InvalidKeyError(Exception):
    pass

isGlobalRLMessageReset = 0

class ModrinthAPI:
    def __init__(self, api_url="https://api.modrinth.com"):
        self.api_url = api_url
        self.utils = utils()
  

    async def get_project(self, url: str):
        response = await self.utils.get(f"{self.api_url}/v2/project/{self.utils.get_slug_by_url(url)}")
        return response



    async def get_project_by_id(self, id: str, *, retries: int = 7):
        try:
            response = await self.utils.get(f"{self.api_url}/v2/project/{id}", retries=retries)
            return response
        except Http404Error:
            return None
    


    async def get_version(self, version_id: str):
        response = await self.utils.get(f"{self.api_url}/v2/version/{version_id}")
        return response
    


    async def project_files(self, project_slug: str, parameters: dict = None):
        query = f"{self.api_url}/v2/project/{project_slug}/version"
        
        if parameters:     
            queryParams = []

            version = parameters.get('game_versions')
            if version:
                queryParams.append(f"game_versions=[{await self.utils.format_query(version)}]")

            loader = parameters.get('loader')
            if loader:
                queryParams.append(f"loaders=[{await self.utils.format_query(loader)}]")
            
            type = parameters.get('version_type')
            if type:
                queryParams.append(f"version_type=[{await self.utils.format_query(type)}]")

            query += '?' + '&'.join(queryParams)
            
        fetchResult = await self.utils.get(query)
        response = sorted(fetchResult, key=lambda x: x['date_published'], reverse=True)
        return response
    


    async def download(self, url: str, *,  parameters: dict = None):
        version = None
        if not url:
            raise ValueError("You must provide a valid url")

        project_slug = self.utils.get_slug_by_url(url)
        versionList = await self.project_files(project_slug, parameters)

        if len(versionList) == 0:
            raise ValueError("No mod versions matching game versions or mod loader found, make sure youve gotten the right mod, and/or that it has a version for said loader/game version")

        version = versionList[0]

        fileUrl = version['files'][0]['url']
        response = await self.utils.Dl_Data(fileUrl)
        return version, response

    




class CurseforgeAPI:
    def __init__(self, api_url="https://api.curseforge.com"):
        
        config = configparser.ConfigParser()
        filePath = os.path.dirname(__file__)
        configPath = os.path.join(filePath, "config", 'config.ini')
        config.read(configPath)
        
        self.api_url = api_url
        self.api_key = config['Curseforge'].get('api_key')
        self.utils = utils()
        
        self.api_headers = {
        'Accept': 'application/json',
        'x-api-key': self.api_key
        }
        
        
        
    async def is_key_valid(self):
        try:
            await self.utils.get(f"{self.api_url}/v1/games", headers=self.api_headers, retries=2)
            return True
        except InvalidKeyError:
            return False



    async def get_project(self, url: str):
        mod_id = await self.get_id_by_url(url)
        return await self.get_project_by_id(mod_id)
    


    async def get_project_by_id(self, id: int, *, retries: int=7):
        response = await self.utils.get(f"{self.api_url}/v1/mods/{id}", headers=self.api_headers, retries=retries)
        return response['data']



    async def get_id_by_url(self, url: str):
        slug = self.utils.get_slug_by_url(url)  
        return await self.get_id_by_slug(slug)
    


    async def get_id_by_slug(self, slug: str):
        data = await self.utils.get(f'{self.api_url}/v1/mods/search', headers=self.api_headers, params={
            'slug': slug,
            'classId': '6',
            'gameId': '432'
        })

        if len(data['data']) > 0:
            result = data['data'][0]['id']
            return result
        else:
            return None


    async def get_slug_by_url(self, url: str):
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



    async def project_files(self, url: str, parameters: dict=None):
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
                files = await self.utils.get(f'{self.api_url}/v1/mods/{id}/files', headers=self.api_headers, params=parameter)
                finalFiles += files['data']
            
        else:        
            files = await self.utils.get(f'{self.api_url}/v1/mods/{id}/files', headers=self.api_headers)
            finalFiles += files['data']

        result = sorted(finalFiles, key=lambda x: x['fileDate'], reverse=True)

        return result
    


    async def download(self, url: str,  *, parameters: dict = None):
        if not url:
            raise ValueError("You must provide a valid url")

        fileList = await self.project_files(url, parameters)

        if len(fileList) == 0:
            raise ValueError("No mod versions matching game versions or mod loader found, make sure youve gotten the right mod, and/or that it has a version for said loader/game version")

        file = fileList[0]

        fileUrl = file['downloadUrl']
        response = await self.utils.Dl_Data(fileUrl)
        return file, response
    

class utils:
    def __init__(self):
        pass
    
    
    
    def get_slug_by_url(self, url: str):
        splitUrl = url.split('/')

        if len(splitUrl) >= 3:
            return splitUrl[-1]
        else:
            raise ValueError("Invalid URL")
        
        
        
    async def get(self, url: str, *, headers: dict = None, params: dict = None, retries: int = 7) -> dict:
        attempt = 0
        async with aiohttp.ClientSession() as session:
            while attempt < retries:        
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        retry_after = response.headers.get('X-Ratelimit-Reset')
                        if 'application/json' in response.headers.get('Content-Type', ''):
                            return await response.json()
                        else:
                            return await response.text()
                    elif response.status == 429:
                        retry_after = response.headers.get('X-Ratelimit-Reset')
                        await self.handle_rate_limit_reset(retry_after)
                    elif response.status == 403:
                        raise InvalidKeyError(f"Invalid api key")
                    elif response.status != 404:
                        raise HttpError(f"Http get error {response.status}: {response.reason}")
                    else:
                        attempt += 1
                await asyncio.sleep(0.5)                   
        raise Http404Error()



    async def handle_rate_limit_reset(self, retry_after: int) -> bool:
        global isGlobalRLMessageReset
        if isGlobalRLMessageReset <= 0:    
            print(f'Too many requests, please wait...')
            isGlobalRLMessageReset += 60
        else:
            isGlobalRLMessageReset -= 1
        if retry_after:
            await asyncio.sleep(int(retry_after) + 5)



    async def Dl_Data(self, url: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers = {"Accept": "application/octet-stream"}) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise Exception(f"Http get error {response.status}: {response.reason}")



    async def format_query(self, query: str):
        formattedQuery = [f'"{x}"' for x in query]
        return ','.join(formattedQuery)