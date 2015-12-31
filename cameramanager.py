import picamera
import io
from imagestream import ImageStream

class CameraManager:
    __cam = picamera.PiCamera()
    
    def capture_picture(self):
        stream = io.BytesIO()
        self.__cam.capture(stream, format='jpeg')
        return ImageStream(stream)