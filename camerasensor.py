import picamera
import io
from imagestream import ImageStream
from sensors import ISensor
from fractions import Fraction

camera = picamera.PiCamera()
camera.awb_mode = 'off'
camera.awb_gains = (Fraction(119, 128), Fraction(631, 256))


class CameraSensor(ISensor):
    
    def capture_picture(self):
        global camera
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')
        return ImageStream(stream)
        
    def update_status(self, status):
        status.picture = self.capture_picture()