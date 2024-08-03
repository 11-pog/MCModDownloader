from MCModDownloader import ModrinthAPI
import asyncio

async def main():
    api = ModrinthAPI()

    project_id = "P7dR8mSH"
    version_id = "Y0cpssyN"

    print('test 1:\n\n\n\n\n')

    project_data = await api.get_project(project_id)
    print(project_data)

    print('test 2:\n\n\n\n\n')

    version_data, mod_file = await api.download_mod(version_id)

    print(version_data)

    print('test 3:\n\n\n\n\n')

    with open(f"{version_data['name']}.jar", "wb") as f:
        f.write(mod_file)

asyncio.run(main())