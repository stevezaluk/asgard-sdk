import hashlib
from logging import exception
import os
from .base import AsgardObject

class GenericFile(AsgardObject):
    def __init__(self, json: dict):
        super(GenericFile, self).__init__(json)

        self.file_name = self.get_value("file_name")
        self.file_location = self.get_value("file_location")
        self.file_size = self.get_value("file_size")
        self.file_type = self.get_value("file_type")
        self.file_sha = self.get_value("file_sha")

        self.uploaded_date = self.get_value("uploaded_date")
        self.uploaded_by = self.get_value("uploaded_by")
        self.creation_date = self.get_value("creation_date")

        self.download_count = self.get_value("download_count")

        self.remote_path = self.file_location + self.file_name

class LocalPathNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class LocalPath(AsgardObject):
    def __init__(self, path: str):
        self.path = path
        self.type = None

        self.validate_path()

        self._stat = os.stat(self.path)
        self._tokens = self.path.split("/")

        self.file_name = self._tokens[-1]
        self.file_location = self.get_location()
        self.file_size = self._stat.st_size
        self.file_type = self.get_asgard_type()
        self.file_sha = None

        self.creation_date = self._stat.st_ctime

    def get_stat(self):
        return self._stat

    def get_path_tokens(self):
        return self._tokens

    def validate_path(self):
        if self.path.startswith("~"):
            self.path = self.path.replace("~", os.getenv("HOME"))

        if os.path.exists(self.path) is False:
            raise LocalPathNotFound("Failed to find Local Path: ", self.path)

        if os.path.isfile(self.path):
            self.type == "file"
        elif os.path.isdir(self.path):
            self.type == "dir"

    def get_location(self):
        tokens = self.get_path_tokens()
        tokens.pop(-1)

        return "/".join(tokens)

    def get_asgard_type(self):
        file_ext = self.file_name.split(".")
        file_ext = "." + file_ext[-1]

        file_type = None

        media_extensions = [".mp4", ".mkv", ".m4v", ".webm", ".mov", ".ts"]
        if file_ext in media_extensions:
            file_type = "video"

        document_extensions = [".pdf", ".txt", ".odt", ".epub", ".doc", ".book"]
        if file_ext in document_extensions:
            file_type = "document"

        game_extensions = [".gb", ".gba", ".nes", ".snes", ".wbfs", ".iso", ".dolphin", ".nkit"]
        if file_ext in game_extensions:
            file_type = "game"

        return file_type
            
    def get_sha(self):
        file_sha = hashlib.sha256()
        with open(self.path, "rb") as file:
            for block in iter(lambda: file.read(4096), b""):
                file_sha.update(block)
        
        file_sha = file_sha.hexdigest()
