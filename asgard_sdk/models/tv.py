from file import GenericFile
from base import generate_object

class TVShow(GenericFile):
    def __init__(self, json: dict):
        super(TVShow, self).__init__(json)
        
        self._root = self.get_json().get("tv_info")

        self.total_seasons = self._root.get("total_seasons")
        self.total_episodes = self._root.get("total_episodes")

        self.seasons = []

    def load_seasons(self):
        seasons = self._root.get("seasons")

        for season in seasons:
            self.seasons.append(generate_object(season))

class Season(GenericFile):
    def __init__(self, json: dict):
        super(Season, self).__init__(json)

        self._root = self.get_json().get("season_info")

        self.episodes = None

    def load_episodes(self):
        episodes = self._root.get("episodes")
