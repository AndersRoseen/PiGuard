import datetime
import factory
from motiondetector import MotionDetector

class Status:
    
    def __init__(self, picture=picture):
        self.timestamp = datetime.datetime.now()
        self.picture = picture
        
        
class StatusHandler:
    
    def __init__(self):
        self.__uploader = factory.get_uploader('piguard.ini')
        self.__mail_sender = factory.get_mail_sender('piguard.ini')
        self.__motion_detector = MotionDetector()
        
    def manage_status(status):
        img_stream = status.picture
        something_changed = motion_detector.detect_motion(img_stream)
    
        if something_changed:
            print("ALARM!!!!!")
            mail_sender.send_mail(img_stream)
        else:
            print("Everything is fine")
    
        uploader.upload_file_stream(img_stream, something_changed)