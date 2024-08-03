from MCModDownloader import ModrinthAPI
import asyncio

async def main():
    api = ModrinthAPI()

    url = 'https://modrinth.com/mod/fabric-api'
    split_url = url.split('/mod/')

    parameters = {
        'game_versions': ['1.20.1'],
        'loader': ['forge']
    }

    if len(split_url) > 1:
        project_versions = await api.project_versions(split_url[1], parameters=parameters)
        print(project_versions)
    else:
        print('Invalid URL')




    '''
    print('test 1:\n\n\n\n\n')

    print('test 2:\n\n\n\n\n')

    version_data, mod_file = await api.download(version_id)

    print(version_data)

    print('test 3:\n\n\n\n\n')

    with open(f"{version_data['name']}.jar", "wb") as f:
        f.write(mod_file)
    '''

asyncio.run(main())