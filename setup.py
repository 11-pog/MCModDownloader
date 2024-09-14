import setuptools

requirements = []

with open("requirements.txt") as f:
    for line in f:
        requirements.append(line)

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
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcmm=mcmm.main:run",
        ],
    },
)
