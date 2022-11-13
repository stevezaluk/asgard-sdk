from .file import File

class Game(File):
    def __init__(self, json: dict = None):
        super(Game, self).__init__(json)

        self.region = None
        self.console = None
