from base import AsgardObject

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
        