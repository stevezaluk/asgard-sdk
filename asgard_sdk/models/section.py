from .base import AsgardObject

class Section(AsgardObject):
    def __init__(self, json: dict):
        super(Section, self).__init__(json)

        self.section_name = self._json.get("section_name")
        self.section_path = self._json.get("section_path")
        self.section_type = self._json.get("section_type")
        self.section_size = self._json.get("section_size")

        self.mongo_collection = self._json.get("mongo_collection")
        self.plex_section = self._json.get("plex_section")

        self.total_downloads = self._json.get("total_downloads")
        self.total_uploads = self._json.get("total_uploads")