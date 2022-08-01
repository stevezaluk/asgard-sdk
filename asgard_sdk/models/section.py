from base import AsgardObject

class Section(AsgardObject):
    def __init__(self, json: dict):
        super(Section, self).__init__(json)

        self.section_name = self.__json.get("section_name")
        self.section_path = self.__json.get("section_path")
        self.section_type = self.__json.get("section_type")
        self.section_size = self.__json.get("section_size")

        self.mongo_collection = self.__json.get("mongo_collection")
        self.plex_section = self.__json.get("plex_section")

        self.total_downloads = self.__json.get("total_downloads")
        self.total_uploads = self.__json.get("total_uploads")