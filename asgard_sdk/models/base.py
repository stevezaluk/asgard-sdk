from file import GenericFile
from video import Video
from document import Document
from game import Game

class AsgardObject(object):
    def __init__(self, json: dict):
        self.__json = json

    def get_json(self):
        return self.__json

    def get_value(self, key: str):
        return self.__json.get(key)

def generate_object(json: dict):
    keys = json.keys()

    ret = GenericFile(json)
    
    # tv, season, episode support
    if "video_info" in keys:
        ret = Video(json)
        if "episode_info" in keys:
            pass

    if "game_info" in keys:
        ret = Game(json)

    if "document_info" in keys:
        ret = Document(json)

    return ret