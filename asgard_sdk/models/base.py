
class AsgardObject(object):
    def __init__(self, json: dict):
        self._json = json

    def get_json(self):
        return self._json

    def get_value(self, key: str):
        return self._json.get(key)