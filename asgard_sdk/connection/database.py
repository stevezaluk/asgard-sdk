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

class Database:
    def __init__(self, ip_address: str, port: int):
        self.ip_address = ip_address
        self.port = port
        
        self._client = None

        self.asgard_db = None
        self.asgard_analytics = None

        self.sections = None

    def _dict_to_response(self, dict: dict):
        return loads(dumps(dict, default=str))

    def build_query(self, term: str):
        query = {}

        sha_regex = re.compile(r'\b[A-Fa-f0-9]{64}\b')
        if sha_regex.match(term):
            query.update({"file_sha":term})
        else:
            query.update({"file_name":term})

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
        database[name]

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
