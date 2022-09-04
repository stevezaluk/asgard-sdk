from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

import re

from json import loads
from bson.json_util import dumps

class MissingDatabase(Exception):
	def __init__(self, message):
		super().__init__(message)

class MissingCollection(Exception):
	def __init__(self, message):
		super().__init__(message)

"""
    Database - Abstraction of a running instance of mongodb

    ip_address (str) - The IP Address of your mongoDB instance
    port (int) - The port of your mongoDB instance

    _client (MongoClient) - The database client for interaction

    asgard_db (pymongo.database.Database) - The main pymongo database that holds all section and file metadata
    asgard_analytics (pymongo.database.Database) - The mongodb database that holds stored analytic data

    sections (pymongo.collection.Collection) - The mongoDB collection that holds all of our sections. I created an instance variable for it, since it is accessed a lot.
"""
class Database:
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
        
        self._client = None

        self.asgard_db = None
        self.asgard_analytics = None

        self.sections = None

    """
        _dict_to_response - Convert mongoDB documents into usable dictionaries.
        
        A method is needed here because having the objectID in the data causes issues.
        The "default" argument in the "dumps" method converts it to a string

        Required Arguments:
            dict (dict) - The dictionary you want to convert

        Returns a dictionary
    """
    def _dict_to_response(self, dict: dict):
        return loads(dumps(dict, default=str))

    """
        build_query - Turn a user given term into a dictionary that we can use to query mongo

        Required Arguments:
            term (str) - Either a file name or a file_sha

        Returns a dictionary
    """
    def build_query(self, term: str):
        query = {}

        sha_regex = re.compile(r'\b[A-Fa-f0-9]{64}\b')
        if sha_regex.match(term):
            query.update({"file_sha":term})
        else:
            query.update({"file_name":term})
        
        return query

    def connect(self) -> None:
        if self._client is None:
            self._client = MongoClient(self.ip_address, self.port)

            self.asgard_db = self.get_database("asgard_db")
            self.asgard_analytics = self.get_database("asgard_analytics")

            self.sections = self.get_collection("sections", self.asgard_db)

    def disconnect(self) -> None:
        if self._client:
            self._client.close()

            self.asgard_db = None
            self.asgard_analytics = None

            self.sections = None

    """
        get_database - Get a pymongo database object by name

        Required Paramaters:
            name (str) - The name of the mongoDB collection you want

        Throws a MissingDatabase exception when it cant be found.
        This is to ensure our database is always formated and created properly

        Returns a pymongo.database.Database object
    """
    def get_database(self, name: str) -> Database:
        ret = None
        
        for database_name in self._client.list_database_names():
            if database_name == name:
                ret = self._client[database_name]
                break

        if ret is None:
            raise MissingDatabase("Cannot find database: {}".format(name))

        return ret

    def create_collection(self, name: str, database: Database):
        return database[name]

    def get_collection(self, name: str, database: Database) -> Collection:
        ret = None
        
        for collection_name in database.list_collection_names():
            if collection_name == name:
                ret = database[collection_name]
                break

        if ret is None:
            raise MissingCollection("Cannot find collection: {}".format(name))

        return ret

    def index_collection(self, collection: Collection) -> list:
        ret = []
        
        documents = collection.find({})
        
        for document in documents:
            document = self._dict_to_response(document)
            ret.append(document)

        return ret

    def get_document(self, query: dict, collection: Collection) -> dict:
        ret = None

        document = collection.find_one(query)

        if document is None:
            return None
        
        ret = self._dict_to_response(document)

        return ret

    def update_document(self, query: dict, update: dict, collection: Collection): # broken
        update_query = {"$set": update}
        result = collection.update_one(query, update)

        matched_count = result.matched_count

        if matched_count == 0:
            return None
        else:
            return matched_count

    def insert_document(self, document: dict, collection: Collection):
        insert_id = collection.insert_one(document).inserted_id

        return insert_id
