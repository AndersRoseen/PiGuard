import picamera
import io
from imagestream import ImageStream
from sensors import ISensor
from fractions import Fraction


class CameraSensor(ISensor):
    
    def __init__(self):
        self._cam = picamera.PiCamera()
        self._cam.awb_mode = 'off'
        self._cam.awb_gains = (Fraction(29, 32), Fraction(869, 256))
    
    def capture_picture(self):
        stream = io.BytesIO()
        self._cam.capture(stream, format='jpeg')
        return ImageStream(stream)
        
    def update_status(self, status):
        status.picture = self.capture_picture()