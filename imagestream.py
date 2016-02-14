from PIL import Image
import io


class ImageStream(object):
    
    def __init__(self, stream: io.BytesIO):
        self._stream = stream
        
    def get_stream(self) -> io.BytesIO:
        self._stream.seek(0)
        return self._stream
    
    def get_image(self) -> Image:
        return Image.open(self.get_stream())
        
    def __del__(self):
        self._stream.close()
