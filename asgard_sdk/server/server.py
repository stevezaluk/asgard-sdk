from ..models.file import File
from ..models.section import Section
from ..models.config import Config
from ..models.handler import ObjectHandler
from ..models import generate_object

from ..connection.plex import Plex
from ..connection.database import Database

"""
    AsgardServer - Abstraction of a running instance of your Server

    config (Config) - The config object containing your mongo and plex values

    _database (Database) - The database object for interacting with file metadata
    _plex (Plex) - The plex object for rescanning sections, and cross checking metadata
"""
class AsgardServer(ObjectHandler):
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

        ret = self.handle_dict(section, key=key, to_dict=to_dict)

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
        
        ret = self.handle_list(sections, key=key, limit=limit, to_dict=to_dict)
        
        return ret

    """
        create_section - Create a new Asgard Section

        Required Paramaters:
            section_name (str) - The name you want your section to have
            remote_path (str) - The remote path that your (media) files are in
            type (str) - The type of section you want to create. Can be video, video-series, games, documents, generic-file

        Optional Paramaters:
            mongo_coll (str) - The name of the mongoDB collection that will hold your file data. Defaults to the name of the section
            plex_section (str) - The name of the plex section that you want to link to the section. Defaults to the name of the section
    
        Returns an Asgard Section object on success, and None on fail

        If none is returned, then the section already exists
    """
    def create_section(self, section_name: str, remote_path: str, type: str, mongo_coll=None, plex_section=None):
        if mongo_coll is None:
            mongo_coll = section_name.lower()

        if plex_section is None:
            plex_section = section_name

        if self.get_section(section_name) is not None:
            return None

        dict = {"section_name":section_name, "section_path":remote_path, 
                "section_type":type, "section_size":0,
                "mongo_collection":mongo_coll, "plex_section":plex_section, 
                "total_downloads":0, "total_uploads":0}

        if type != "video" or type != "video-series":
            dict.pop("plex_section", None)

        mongo_coll = self._database.create_collection(mongo_coll, self._database.asgard_db)
        insert_id = self._database.insert_document(dict, self._database.sections)

        section = Section(dict)

        return section
    
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
            for section in self.get_sections(): # test this
                mongo_collection = section.mongo_collection

                file = self._database.get_document(query, self._database.get_collection(mongo_collection, self._database.asgard_db))

                if file is not None:
                    break
        
        ret = self.handle_dict(file, key=key, to_dict=to_dict)

        if plex:
            pass

        return ret

    """
        register_file - Insert a files metadata into the database. This does not upload

        Required Paramaters:
            file (GenericFile) - The file object you want to insert
            section (Section) - The section object you want to upload to

        Returns None on fail, and a tuple of the file and the insert_id on success
    """
    def register_file(self, file: File, section: Section):
        if section.section_type != file.file_type:
            return None 

        mongo_collection = self._database.get_collection(section.mongo_collection, self._database.asgard_db)
        insert_id = self._database.insert_document(file.get_json(), mongo_collection)

        section_size = section.section_size + file.file_size
        total_uploads = section.total_uploads + 1

        self._database.update_document({"section_name":section.section_name}, {"section_size":section_size}, self._database.sections)
        self._database.update_document({"section_name":section.section_name}, {"total_uploads":total_uploads}, self._database.sections)

        self._database.insert_document(file.get_json(), self._database.get_collection("recently_uploaded", self._database.asgard_analytics))

        return file

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
            index = []
            for section in self.get_sections(limit=limit):
                mongo_collection = section.mongo_collection

                index = index + self._database.index_collection(self._database.get_collection(mongo_collection, self._database.asgard_db))

        ret = self.handle_list(index, key=key, limit=limit, to_dict=to_dict)

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
                    document = self.get_obj_from_dict(document)
                elif (key is not None and key in document.keys()):
                    document = document.get(key)
                
                ret.append(document)

        return ret

    def get_popular(self, key: str = None, limit: int = 15, to_dict: bool = False):
        popular = self._database.index_collection(self._database.get_collection("popular", self._database.asgard_analytics))

        ret = self.handle_list(popular, key=key, limit=limit, to_dict=to_dict)

        return ret

    def get_recently_uploaded(self, key: str = None, limit: int = 15, to_dict: bool = False):
        recently_uploaded = self._database.index_collection(self._database.get_collection("recently_uploaded", self._database.asgard_analytics))

        ret = self.handle_list(recently_uploaded, key=key, limit=limit, to_dict=to_dict)

        return ret

    def get_recently_downloaded(self, key: str = None, limit: int = 15, to_dict: bool = False):
        recently_downloaded = self._database.index_collection(self._database.get_collection("recently_downloaded", self._database.asgard_analytics))

        ret = self.handle_list(recently_downloaded, key=key, limit=limit, to_dict=to_dict)
            
        return ret

    def get_favorites(self, key: str = None, limit: int = 15, to_dict: bool = False):
        favorites = self._database.index_collection(self._database.get_collection("favorites", self._database.asgard_analytics))

        ret = self.handle_list(favorites, key=key, limit=limit, to_dict=to_dict)
            
        return ret

    def get_feature_file(self, key: str = None, limit: int = 15, to_dict: bool = False, plex: bool = False):
        feature_file = self._database.get_document({}, self._database.get_collection("feature", self._database.asgard_analytics))

        ret = self.handle_dict(feature_file, key=key, limit=limit, to_dict=to_dict)

        return ret
