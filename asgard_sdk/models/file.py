from distutils.command.upload import upload
from ..models.local import LocalPath
from .base import AsgardObject

import datetime

class File(AsgardObject):
    def __init__(self, json: dict = None):
        super(File).__init__(json)

        self.file_name = None
        self.file_ext = None
        self.file_location = None
        self.file_size = None

        self.file_type = None
        self.file_sha = None

        self.home_section = None

        self.upload_meta = None
    
    def get_size_string(self, bytes: int):
        size = round(bytes / 1000000, 2)
        size_str = "{mb} MB".format(mb=size)

        if size >= 1000.00:
            size = round(size / 1000, 2)
            size_str = "{gb} GB".format(gb=size)
        
        return size_str