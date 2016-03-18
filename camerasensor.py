import picamera
import io
from imagestream import ImageStream
from sensors import ISensor
import configmanager
from piguardtyping import Status


camera = picamera.PiCamera()


def capture_picture() -> ImageStream:
    global camera
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg')
    return ImageStream(stream)


def setup_camera():
    global camera
    camera.resolution = (int(configmanager.config["picamera"]["resolution"].split("x")[0]),
                         int(configmanager.config["picamera"]["resolution"].split("x")[1]))
    camera.rotation = int(configmanager.config["picamera"]["rotation"])

setup_camera()


class CameraSensor(ISensor):
        
    def update_status(self, status: Status):
        status["picture"] = capture_picture()
