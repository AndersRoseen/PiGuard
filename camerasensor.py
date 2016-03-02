import picamera
import io
from imagestream import ImageStream
from sensors import ISensor
import configmanager
from piguardtyping import Status


camera = picamera.PiCamera()
#camera.awb_mode = 'off'
#camera.awb_gains = (Fraction(119, 128), Fraction(631, 256))


def setup_camera():
    global camera
    camera.resolution = (int(configmanager.config["picamera"]["resolution"].split("x")[0]),
                         int(configmanager.config["picamera"]["resolution"].split("x")[1]))
    camera.rotation = int(configmanager.config["picamera"]["rotation"])


class CameraSensor(ISensor):

    def __init__(self):
        setup_camera()
    
    def capture_picture(self) -> ImageStream:
        global camera
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')
        return ImageStream(stream)
        
    def update_status(self, status: Status):
        status["picture"] = self.capture_picture()
