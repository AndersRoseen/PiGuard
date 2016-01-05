import picamera
import io
from imagestream import ImageStream
from sensors import ISensor

class CameraSensor(ISensor):
    _cam = picamera.PiCamera()
    
    def capture_picture(self):
        stream = io.BytesIO()
        self._cam.capture(stream, format='jpeg')
        return ImageStream(stream)
        
    def update_status(self, status):
        status.picture = self.capture_picture()