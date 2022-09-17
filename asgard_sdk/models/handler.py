from ..models.local import LocalPath
from ..models.file import GenericFile
from ..models.video import Video
from ..models.document import Document
from ..models.game import Game

from ..models.section import Section

from pymediainfo import MediaInfo
from ebooklib import epub
from PyPDF2 import PdfReader

class ObjectHandler:

    def get_obj_from_dict(self, dict: dict):
        ret = None

        keys = dict.keys()
        if "file_name" in keys:
            ret = GenericFile(dict)

            if "video_info" in keys:
                ret = Video(dict)
            elif "document_info" in keys:
                ret = Document(dict)
            elif "game_info" in keys:
                ret = Game(dict)
            # video-series

        if "section_name" in keys:
            ret = Section(dict)

        return ret

    def get_obj_from_local(self, local_path:LocalPath):
        file_dict = local_path.get_dict()

        ret = None
        if local_path.file_type == "video":
            media_info = MediaInfo.parse(local_path.path)

            video_info = {}
            video_track_count = 0
            audio_track_count = 0
            for track in media_info.tracks:
                if track.track_type == "General":
                    video_info.update({"duration":track.duration})
                    video_info.update({"format":track.format})

                if track.track_type == "Video":
                    video_track_count += 1
                    video_info.update({"video_codec":track.codec_id})
                    video_info.update({"resoloution":"{w}x{h}".format(w=track.width, h=track.height)})

                if track.track_type == "Audio":
                    audio_track_count += 1
                    video_info.update({"audio_codec":track.codec_id})
                    video_info.update({"language":track.other_language})
                
            file_dict.update({"video_track_count":video_track_count})
            file_dict.update({"audio_track_count":audio_track_count})

            file_dict.update({"video_info":video_info})
            ret = Video(file_dict)
        elif local_path.file_type == "document":
            document_info = {}
            
            if local_path.file_ext == ".epub":
                book = epub.read_epub(self.path)
                
                document_info.update({"title":book.title})
                document_info.update({"author":book.get_metadata("DC", 'creator')})
                document_info.update({"format":"E-PUB"})
                document_info.update({"page_count":len(book.pages)})
            elif local_path.file_ext == ".pdf":
                book = PdfReader(self.path)

                document_info.update({"title":book.metadata.title})
                document_info.update({"author":book.metadata.author})

                document_info.update({"format":"Portable Document Format (PDF)"})
                document_info.update({"page_count":len(book.pages)})

            file_dict.update({"document_info":document_info})
            ret = Document(file_dict)
        
        return ret
