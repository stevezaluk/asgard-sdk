from .base import AsgardObject

class Section(AsgardObject):
    def __init__(self, json: dict = None):
        super(Section, self).__init__(json)

        self.section_name = None
        self.section_path = None
        self.section_type = None
        self.section_size = None

        self.mongo_collection = None
        self.plex_section = None

        self.total_downloads = None
        self.total_uploads = None