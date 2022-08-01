from file import GenericFile

class Game(GenericFile):
    def __init__(self, json: dict):
        super(Game, self).__init__(json)

        self._root = self.get_json().get("game_info")

        self.region = self._root.get("region")
        self.console = self._root.get("console")
