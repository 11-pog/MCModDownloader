import setuptools

with open("README.md", "r") as f:
    long_description = f.read()
    
setuptools.setup(
    name="mcmm",
    version="0.1a5",
    author="OpinionThief",
    author_email="",
    description="A package to download Minecraft mods from Modrinth and Curseforge, comes with free spaghetti (code)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/11-pog/MCModDownloader",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "aiohttp>=3.10.5",
        "emoji>=2.12.1",
        "furl>=2.1.3",
        "setuptools>=74.0.0"
        ],
    entry_points={
        "console_scripts": [
            "mcmm=mcmm.main:run",
        ],
    },
)
