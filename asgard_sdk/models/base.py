
class AsgardObject(object):
    def __init__(self, json: dict = None):
        self.__json = json
        self.__insert_id = None

    def get_insert_id(self):
        return self.__insert_id

    def get_json(self):
        return self.__json

    def get_value(self, key: str):
        ret = None
        
        if self.__json is not None:
            ret = self.__json.get(key)

        return ret