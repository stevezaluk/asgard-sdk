from file import GenericFile

class Document(GenericFile):
    def __init__(self, json: dict):
        super(Document, self).__init__(json)

        self._root = self.get_json().get("document_info")

        self.format = self._root.get("format")
        self.title = self._root.get("title")
        self.author = self._root.get("author")
        self.page_count = self._root.get("page_count")
