import io
from PIL import Image

class ImageStream:
    
    def __init__(self, stream):
        self.__stream = stream
        
    def get_stream(self):
        self.__stream.seek(0)
        return self.__stream
    
    def get_image(self):
        return Image.open(self.get_stream())
        
    def __del__(self):
        self.__stream.close()