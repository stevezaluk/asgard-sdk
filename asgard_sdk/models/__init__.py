from .section import Section
from .file import File
from .video import Video
from .document import Document
from .game import Game

def generate_object(json: dict):
    keys = json.keys()

    if "section_name" in keys:
        return Section(json)

    if "file_name" in keys:
        ret = File(json)
    
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