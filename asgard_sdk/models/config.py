from .file import LocalPath

from dotenv import dotenv_values

class ConfigError(Exception):
	def __init__(self, message):
		super().__init__(message)

"""
    Config - Object for server side config file
    
    path (str) : The path to your file
    values (dict) : Dictionary returned from dotenv_values.
    
    mongo_ip (str) : IP Address of your running mongoDB instance
    mongo_port (int) : The port of your running mongoDB instance

    plex_ip (str) : The IP Address of your running plex instance
    plex_port (str) : The port of your running plex instance

    plex_token (str) : Access code to send with requests to the plex REST API
"""
class Config(LocalPath): # untested
    def __init__(self, path: str):
        super(Config, self).__init__(path)

        self.values = None

        self.validate_file()

        self.mongo_ip = self.values.get("MONGO_IP")
        self.mongo_port = self.values.get("MONGO_PORT")

        self.plex_ip = self.values.get("PLEX_IP")
        self.plex_port = self.values.get("PLEX_PORT")
        self.plex_token = self.values.get("PLEX_TOKEN")

    def validate_file(self):        
        if self.type == "dir" or self.type == None:
            raise ConfigError("Config must be a file")

        self.values = dotenv_values(self.path)

    def validate_structure(self):
        if self.mongo_ip is None or self.mongo_port is None:
            raise ConfigError("Missing mongoDB information")

        if self.plex_ip is None or self.plex_port is None:
            raise ConfigError("Missing plex information")

        if self.plex_token is None:
            raise ConfigError("Missing plex token. See https://www.plex.tv on how to get one")
