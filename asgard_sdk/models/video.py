from file import GenericFile

class Video(GenericFile):
    def __init__(self, json: dict):
        super(Video, self).__init__(json)

        self._root = self.get_json().get("video_info")

        self.resolution = self._root.get("resolution")
        self.format = self._root.get("format")
        self.video_codec = self._root.get("video_codec")
        self.audio_codec = self._root.get("audio_codec")
        self.language = self._root.get("language")
        self.duration = self._root.get("duration")
