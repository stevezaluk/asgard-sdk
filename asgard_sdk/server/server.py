from ..connection.database import Database
from ..models.config import Config
from ..models import generate_object

class AsgardServer(object):
    def __init__(self, config: Config):
        self.config = config # pre-validated config

        self._database = Database(config.mongo_ip, config.mongo_port)
        self._plex = None

    def connect(self):
        self._database.connect()

    def disconnect(self):
        self._database.disconnect()

    def get_section(self, section_name: str, key=None, to_dict=False):
        section = self._database.get_document({"section_name":section_name}, self._database.sections)
        if section is None:
            return None

        if to_dict:
            return section
        
        if key:
            pass

        ret = generate_object(section)

        return ret 

    def get_sections(self, key=None, limit=15, sort=None, to_dict=False):
        sections = self._database.index_collection(self._database.sections)
        if to_dict:
            return sections

        if key:
            pass
        
        ret = []
        for section in sections:
            ret.append(generate_object(section))

        return ret

    def get_file(self, term: str, section_name=None, key=None, plex=False, to_dict=False):
        query = self._database.build_query(term)
        
        if section_name is not None:
            section = self.get_section(section_name) # wrap this
            if section is None:
                return None

            file = self._database.get_document(query, self._database.get_collection(section.mongo_collection))
        else:
            raise NotImplementedError("Only retrieval from a single section works for now. Implementation planned by August 10th")

        if file is None:
            return None
        
        if to_dict:
            return file

        if plex:
            pass

        ret = generate_object(file)

        return ret
    
    def index(self, section_name=None, key=None, limit=15, sort=None, to_dict=False):
        if section is not None:
            section = self.get_section(section_name)
            if section is None:
                return None
            
            index = self._database.index_collection(self._database.get_collection(section.mongo_collection))
        else:
            raise NotImplementedError("Only retrieval from a single section works for now. Implementation planned by August 10th")

        if to_dict:
            return index
        
        ret = []
        for document in index:
            ret.append(generate_object(document))

        return ret
    
    def search(self, file_name: str, section_name=None, key=None, limit=15, sort=None, to_dict=False):
        pass