from setuptools import setup, find_packages


VERSION = '1.0.2'
DESCRIPTION = 'This is a bilibili down class with search and download functions'
LONG_DESCRIPTION = 'Bilibili down class not only can search audio , but also can input videoID (such as :BV1x84y1H7mG) to download video or audio'

# Setting up
setup(
    name="chen_bilibili_download",
    version=VERSION,
    author="Chen_Station_B_Cuadaa",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'bilibili', 'download','windows'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
