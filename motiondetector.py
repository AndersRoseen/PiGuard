from camerasensor import CameraSensor
from PIL import ImageChops
from functools import reduce
import math 
import operator
from status import IStatusAnalyzer, Event

class MotionDetector(IStatusAnalyzer):
    
    def __init__(self):
        #cm = CameraSensor()
        #self.__last_picture_stream = cm.capture_picture()
        self.__last_picture_stream = None
    
    @staticmethod
    def __img_diff(im1, im2):
        h = ImageChops.difference(im1, im2).histogram()
        return math.sqrt(reduce(operator.add, map(lambda h, i: h*(i**2), h, range(256)))/(float(im1.size[0])*im1.size[1]))
        
    def __detect_motion(self, new_picture_stream):
        
        if self.__last_picture_stream is None:
            self.__last_picture_stream = new_picture_stream
            return False
        
        im1 = self.__last_picture_stream.get_image()
        im2 = new_picture_stream.get_image()
        mean_diff = MotionDetector.__img_diff(im1, im2)
        
        motion_occurred = mean_diff > 10
        
        self.__last_picture_stream = new_picture_stream
        
        if motion_occurred:
            print("motion status: Motion detected!")
        else:
            print("motion status: Everything is quiet!")
        
        return motion_occurred
        
    
    def analyze_status(self, status):
        events = []
        if self.__detect_motion(status.picture):
            events.append(Event.motionDetected)
        return events