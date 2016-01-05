from camerasensor import CameraSensor
from PIL import ImageChops
from functools import reduce
import math 
import operator
from status import IStatusAnalyzer, Event

class MotionDetector(IStatusAnalyzer):
    
    def __init__(self):
        self._last_picture_stream = None
    
    def _img_diff(self, im1, im2):
        h = ImageChops.difference(im1, im2).histogram()
        return math.sqrt(reduce(operator.add, map(lambda h, i: h*(i**2), h, range(256)))/(float(im1.size[0])*im1.size[1]))
        
    def _detect_motion(self, new_picture_stream):
        
        if self._last_picture_stream is None:
            self._last_picture_stream = new_picture_stream
            return False
        
        im1 = self._last_picture_stream.get_image()
        im2 = new_picture_stream.get_image()
        mean_diff = self._img_diff(im1, im2)
        
        motion_occurred = mean_diff > 10
        
        self._last_picture_stream = new_picture_stream
        
        if motion_occurred:
            print("motion status: Motion detected!")
        else:
            print("motion status: Everything is quiet!")
        
        return motion_occurred
        
    
    def analyze_status(self, status):
        if self._detect_motion(status.picture):
            return [Event.motionDetected]
        return []