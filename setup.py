import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SeisWaveDownloader",
    version="0.1.0",
    author="YJie",
    author_email="jieyaqi@msu.edu",
    description="Download seismic data from IRIS parallelly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com:Aaaapril4/SeisWaveDownloader.git",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'seiswave=seiswavedownloader:main',
        ],
    },
)