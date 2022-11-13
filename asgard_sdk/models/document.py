from .file import File

class Document(File):
    def __init__(self, json: dict = None):
        super(Document, self).__init__(json)

        self.title = None
        self.author = None
        self.identifier = None
        self.format = None