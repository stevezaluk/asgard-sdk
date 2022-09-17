import hashlib
import os

class LocalPathNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

class LocalPath(object):
    def __init__(self, path: str):
        self.path = path
        self.type = None

        self.validate_path()

        self._stat = os.stat(self.path)
        self._tokens = self.path.split("/")

        self.file_name = self._tokens[-1]
        self.file_ext = "." + self.file_name.split(".")[-1]
        self.file_location = self.get_location()
        self.file_size = self._stat.st_size # do recursive file size for directory sizes
        self.file_type = self.get_asgard_type()
        self.file_sha = None

        self.creation_date = self._stat.st_ctime

    def get_stat(self):
        return self._stat

    def get_path_tokens(self):
        return self._tokens

    def get_dict(self):
        dict = {"file_name":self.file_name, "file_location":self.file_location, "file_size":self.file_size,
                "file_type":self.file_type, "file_sha":self.get_sha(), "creation_date":self.creation_date}

        return dict

    def validate_path(self):
        if self.path.startswith("~"):
            self.path = self.path.replace("~", os.getenv("HOME"))

        if os.path.exists(self.path) is False:
            raise LocalPathNotFound("Failed to find Local Path: ", self.path)

        if os.path.isfile(self.path):
            self.type = "file"
        elif os.path.isdir(self.path):
            self.type = "dir"

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

        if file_type is None:
            file_type = "generic-file"

        if self.type == "dir":
            file_type = "video-series"

        return file_type
            
    def get_sha(self):
        file_sha = hashlib.sha256()
        with open(self.path, "rb") as file:
            for block in iter(lambda: file.read(4096), b""):
                file_sha.update(block)
        
        self.file_sha = file_sha.hexdigest()

        return self.file_sha
