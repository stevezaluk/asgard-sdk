from ..format.print import print_error

from ..models import generate_object
from ..models.config import ClientConfig
from ..models.section import Section

from json import loads
from requests import Session

class FailedToFindResource(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidContentType(Exception):
    def __init__(self, message):
        super().__init__(message)
    
class InternalServerError(Exception):
    def __init__(self, message):
        super().__init__(message)

class AsgardClient(object):
    def __init__(self, config: ClientConfig):
        self.config = config
        self.config.validate_structure()

        self._session = Session()

        self.base_url = "http://{ri}:{rp}/api/v1".format(ri=self.config.rest_ip, rp=self.config.rest_port)
        self.anayltics_url = "http://{ri}:{rp}/api/analytics".format(ri=self.config.rest_ip, rp=self.config.rest_port)

        # self._cache_info()

    def _query(self, endpoint, params=None, content_type="application/json", analytics=False):
        if analytics:
            url = self.anayltics_url + "/" + endpoint
        else:
            url = self.base_url + "/" + endpoint
        
        resp = self._session.get(url, params=params)
        
        if resp.status_code == 404:
            raise FailedToFindResource("Failed to find resource: {}".format(url))

        if resp.status_code == 500:
            raise InternalServerError("Internal server error")
        
        if resp.headers.get("Content-Type") != content_type:
            raise InvalidContentType("Content type != {}".format(content_type))

        if content_type == "application/json":
            resp = loads(resp.content)

        return resp

    def _cache_info(self):
        resp = self._query("version", analytics=True)

        self.config.cached_info = resp

    """
    """
    def get_sections(self, key: str = None, limit: int = 15, sort: str = None, to_dict: bool = False):
        params = {}
        if key:
            params.update({"key":key})

        if limit:
            params.update({"limit":limit})

        if sort:
            params.update({"sort":sort})

        resp = self._query("sections", params=params)

        sections = resp.get("sections")
        if to_dict:
            return sections

        ret = []

        for section in sections:
            section = generate_object(section)
            ret.append(section)

        return ret

    def get_section(self, section_name: str, key: str = None, to_dict: bool = False):
        params = {}

        if key:
            params.update({"key":key})
        
        url = "section/" + section_name        
        section = self._query(url, params=params)

        if to_dict:
            return section

        return generate_object(section)

    def get_file(self, term: str, section: Section = None, key: str = None, plex: bool = False, to_dict: bool = False):
        params = {}
        if key:
            params.update({"key":key})

        if plex:
            params.update({"plex":True})

        url = "file/"
        if section:
            url = url + section.section_name + "/"

        file = self._query(url + term, params=params)

        if to_dict:
            return file

        return generate_object(file)

    def index(self, section: Section = None, key: str = None, limit: int = 15, sort: str = None, to_dict: bool = False):
        params = {}

        if key:
            params.update({"key":key})

        if limit:
            params.update({"limit":limit})
        
        url = "index"
        if section:
            url = url + ("/" + section.section_name)
        
        resp = self._query(url, params=params)

        index = resp.get("index")

        if to_dict:
            return index

        ret = []

        for file in index:
            file = generate_object(file)
            ret.append(file)

        return ret


    def search(self, file_name: str, section: Section = None, key: str = None, limit: int = 15, sort: str = None, to_dict: bool = False):
        params = {"q":file_name}

        if key:
            params.update({"key":key})

        if limit:
            params.update({"limit":limit})

        url = "search/"
        if section:
            url = url + section.section_name

        resp = self._query(url, params=params)

        search = resp.get("search")

        if to_dict:
            return search

        ret = []

        for file in search:
            file = generate_object(file)
            ret.append(file)

        return ret