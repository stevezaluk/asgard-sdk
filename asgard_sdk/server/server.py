from asgard_sdk.models.base import AsgardObject
from asgard_sdk.models.file import GenericFile
from asgard_sdk.models.section import Section
from ..connection.plex import Plex
from ..connection.database import Database

from ..models.config import Config
from ..models import generate_object

"""
    AsgardServer - Abstraction of a running instance of your Server

    config (Config) - The config object containing your mongo and plex values

    _database (Database) - The database object for interacting with file metadata
    _plex (Plex) - The plex object for rescanning sections, and cross checking metadata
"""
class AsgardServer(object):
    def __init__(self, config: Config):
        self.config = config # pre-validated config

        self._database = Database(config.mongo_ip, int(config.mongo_port))
        self._plex = Plex(config.plex_ip, config.plex_port, config.plex_token)

    def get_database(self):
        return self._database
    
    def get_plex(self):
        return self._plex

    def connect(self):
        self._database.connect()

    def disconnect(self):
        self._database.disconnect()

    """
        get_section - Retrieve section metadata from the database

        Required Paramaters:
            section_name (str) - The name of the section you want to retreieve

        Optional Paramaters:
            key (str) - Return the value of the key you pass
            to_dict (bool) - Returns the raw JSON document

        Returns None on fail, and either a dict or a AsgardObject on success
        
        Returns None if the section cant be found
        Returns a dictionary if to_dict is True
        Returns a Section object if it can be found
    """
    def get_section(self, section_name: str, key: str = None, to_dict: bool = False):
        section = self._database.get_document({"section_name":section_name}, self._database.sections)
        if section is None:
            return None

        if to_dict:
            return section
        
        if key:
            pass

        ret = generate_object(section)

        return ret

    """
        get_sections - Retrieve all section documents from the database

        Optional Paramaters:
            key (str) - Return the value of the key you pass
            limit (int) - Limit the number of documents you return
            sort (str) - Sort your data in a specific way. Posiblities: alph, asc, desc
            to_dict (bool) - Returns the raw JSON document if true
        
        Returns an empty list if you have no sections
        Returns a list of Section objects if you do
        Returns a list of dict's if its true
    """
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
    
    """
        get_file - Retrieve a single file's metadata from the database

        Required Paramaters:
            term (str) - Either a file name or a SHA-256 hash 
        
        Optional Paramaters:
            section (Section) - Limit your search to within a section
            key (str) - Return the value of the key you pass
            plex (bool) - Return plex metadata with asgard metadata
            to_dict (bool) - Returns the raw JSON document if true
        
        Returns None if the file cant be found
        Returns a dict if "to_dict" is true
        Returns a AsgardObject any other time
    """
    def get_file(self, term: str, section: Section = None, key: str = None, plex: bool = False, to_dict: bool= False):
        query = self._database.build_query(term)
        
        if section is not None:
            file = self._database.get_document(query, self._database.get_collection(section.mongo_collection, self._database.asgard_db))
        else:
            raise NotImplementedError("Only retrieval from a single section works for now. Implementation planned by August 10th")

        if file is None:
            return None
        
        if to_dict:
            return file

        if (key is not None and key in file.keys()):
            ret = file.get(key)
        else:
            ret = generate_object(file)

        if plex:
            pass

        return ret

    """
        create_file - Insert a files metadata into the database. This does not upload

        Required Paramaters:
            file (GenericFile) - The file object you want to insert
            section (Section) - The section object you want to upload to

        Returns None on fail, and a tuple of the file and the insert_id on success
    """
    def create_file(self, file: GenericFile, section: Section):
        if section.section_type != file.file_type:
            return None

        mongo_collection = self._database.get_collection(section.mongo_collection)
        insert_id = self._database.insert_document(file.get_json(), mongo_collection)

        return file, insert_id

    """
        index - Retrieve all file metadata available

        Optional Paramaters:
            section_name (str) - Limit your index to a specific section
            key (str) - Return the value of the key you pass
            limit (int) - Limit the number of documents you return
            sort (str) - Sort your data in a specific way. Posiblities: alph, asc, desc
            to_dict (bool) - Returns the raw JSON document if true

        Returns None on fail, and a list of either dictionaries or AsgardObjects on success
    """
    def index(self, section: Section = None, key: str = None, limit: int = 15, sort: str = None, to_dict: bool = False):
        if section is not None:
            index = self._database.index_collection(self._database.get_collection(section.mongo_collection, self._database.asgard_db))
        else:
            raise NotImplementedError("Only retrieval from a single section works for now. Implementation planned by August 10th")

        if to_dict:
            return index

        ret = []
        for document in index:
            if (key is not None and key in document.keys()):
                document = document.get(key)
            else:
                document = generate_object(document)
            
            ret.append(document)

        return ret
    
    """
        search - Search for a file by file name

        Optional Paramaters:
            section (Section) - Limit your index to a specific section
            key (str) - Return the value of the key you pass
            limit (int) - Limit the number of documents you return
            sort (str) - Sort your data in a specific way. Posiblities: alph, asc, desc
            to_dict (bool) - Returns the raw JSON document if true

        Returns None on fail, and a list of either dictionaries or AsgardObjects on success
    """    
    def search(self, file_name: str, section: Section = None, key: str = None, limit: int = 15, sort: str = None, to_dict: bool = False):
        index = self.index(section, to_dict=True)

        if index is None:
            return None

        ret = []

        for document in index:
            real_file_name = document.get("file_name")
            
            if real_file_name is None:
                pass
            elif file_name in real_file_name:
                if to_dict is False:
                    document = generate_object(document)
                elif (key is not None and key in document.keys()):
                    document = document.get(key)
                
                ret.append(document)

        return ret
