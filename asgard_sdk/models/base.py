
class AsgardObject(object):
    def __init__(self, json: dict):
        self.__json = json

    def get_json(self):
        return self.__json

    def get_value(self, key: str):
        return self.__json.get(key)