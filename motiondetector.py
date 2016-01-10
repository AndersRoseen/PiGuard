from camerasensor import CameraSensor
from PIL import ImageChops
from functools import reduce
import math 
import operator
from status import IStatusAnalyzer, Event


def img_diff(im1, im2):
    histogram = ImageChops.difference(im1, im2).histogram()
    rms = reduce(operator.add, map(lambda h, i: h*(i**2), histogram, range(256)))/(float(im1.size[0])*im1.size[1])
    return math.sqrt(rms)


class MotionDetector(IStatusAnalyzer):
    
    def __init__(self):
        self._last_picture_stream = None

    def _detect_motion(self, new_picture_stream):
        
        if self._last_picture_stream is None:
            self._last_picture_stream = new_picture_stream
            return False
        
        im1 = self._last_picture_stream.get_image()
        im2 = new_picture_stream.get_image()
        mean_diff = img_diff(im1, im2)
        
        motion_occurred = mean_diff > 10
        
        self._last_picture_stream = new_picture_stream
        
        if motion_occurred:
            print("motion status: Motion detected! ", mean_diff)
        else:
            print("motion status: Everything is quiet! ", mean_diff)
        
        return motion_occurred

    def analyze_status(self, status):
        if self._detect_motion(status.picture):
            return [Event.motionDetected]
        return []