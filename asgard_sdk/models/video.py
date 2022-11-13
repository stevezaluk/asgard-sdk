from .file import File

class Video(File):
    def __init__(self, json: dict = None):
        super(Video, self).__init__(json)

        self.duration = None
        self.format = None
        self.resoloution = None
        self.video_codec_id = None
        self.video_mime_type = None
        self.audio_codec_id = None

        self.subtitle_count = None
        
        self.languages = None