from .base import AsgardObject

from os import getenv
from os.path import exists, isfile

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
class Config(AsgardObject): # untested
    def __init__(self, path: str):
        self.path = path
        self.values = None
        self.validate_path()
        
        super(Config, self).__init__(self.values)

        self.mongo_ip = self.get_value("MONGO_IP")
        self.mongo_port = self.get_value("MONGO_PORT")

        self.plex_ip = self.get_value("PLEX_IP")
        self.plex_port = self.get_value("PLEX_PORT")
        self.plex_token = self.get_value("PLEX_TOKEN")

    def validate_path(self):
        if self.path.startswith("~"):
            self.path = self.path.replace("~", getenv("HOME"))

        if exists(self.path) is False:
            raise ConfigError("Config path not found: {}".format(self.path))
        
        if isfile(self.path) is False:
            raise ConfigError("Config must be a file")

        self.values = dotenv_values(self.path)

    def validate_structure(self):
        if self.mongo_ip is None or self.mongo_port is None:
            raise ConfigError("Missing mongoDB information")

        if self.plex_ip is None or self.plex_port is None:
            raise ConfigError("Missing plex information")

        if self.plex_token is None:
            raise ConfigError("Missing plex token. See https://www.plex.tv on how to get one")
