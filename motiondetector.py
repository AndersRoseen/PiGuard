from cameramanager import CameraManager
from PIL import ImageChops
from functools import reduce
import math, operator

class MotionDetector:
    
    def __init__(self):
        cm = CameraManager()
        self.__last_picture_stream = cm.capture_picture()
    
    @staticmethod
    def __img_diff(im1, im2):
        h = ImageChops.difference(im1, im2).histogram()
        return math.sqrt(reduce(operator.add, map(lambda h, i: h*(i**2), h, range(256)))/(float(im1.size[0])*im1.size[1]))
        
    def detect_motion(self, new_picture_stream):
        im1 = self.__last_picture_stream.get_image()
        im2 = new_picture_stream.get_image()
        mean_diff = MotionDetector.__img_diff(im1, im2)
        
        motion_occurred = mean_diff > 10
        
        self.__last_picture_stream = new_picture_stream
        
        return motion_occurred