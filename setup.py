import setuptools

setuptools.setup(name="asgard-sdk", 
                version="1.0", 
                description="A SDK for asgard",
                url="https://github.com/stevezaluk/asgard-sdk",
                install_requires=["pymongo", "plexapi", "colorama", "requests", "bson"],
                python_requires='>=3')
