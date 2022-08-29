from plexapi.server import PlexServer

class Plex(object):
    def __init__(self, ip_address: str, port: int, token=None):
        self.ip_address = ip_address
        self.port = port
        self.token = token

        self._server = None
        self.library = None
        self.sections = None

        self.base_url = "http://{i}:{p}".format(i=self.ip_address, p=self.port)

    def connect(self):
        if self._server is None:
            self._server = PlexServer(baseurl=self.base_url, token=self.token)
            self.library = self._server.library
            self.sections = self._server.library.sections()

    def disconnect(self):
        if self._server is not None:
            self._server = None
            self.library = None
            self.sections = None

    def get_item_key(self, file_name):
        for section in self.sections:
            for item in section.search():
                name = item.locations[0]
                name = name.split("/")[-1]

                if name == file_name:
                    return item, item.key

    def scan(self, section_name=None):
        for section in self.sections:
            if section_name:
                if section.title == section_name:
                    section.update()
            else:
                section.update()

    def refresh_metadata(self, section_name=None):
        for section in self.sections:
            if section_name:
                if section.title == section_name:
                    section.refresh()
            else:
                section.refresh()
    
    def optimize(self, section_name=None):
        for section in self.sections:
            if section_name:
                if section.title == section_name:
                    section.optimize()
            else:
                section.optimize()