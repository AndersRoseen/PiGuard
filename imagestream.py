import io
from PIL import Image

class ImageStream(object):
    
    def __init__(self, stream):
        self._stream = stream
        
    def get_stream(self):
        self._stream.seek(0)
        return self._stream
    
    def get_image(self):
        return Image.open(self.get_stream())
        
    def __del__(self):
        self._stream.close()