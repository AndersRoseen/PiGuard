import datetime
import factory

class Status:
    
    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.picture = None
        

class StatusGenerator:
    
    def __init__(self):
        self.__sensors = factory.get_sensors()
    
    def get_current_status(self):
        status = Status()
        for sensor in self.__sensors:
            sensor.update_status(status)
        
        return status


class StatusHandler:
    
    def __init__(self):
        self.__uploader = factory.get_uploader()
        self.__mail_sender = factory.get_mail_sender()
        self.__motion_detector = factory.get_motion_detector()
        
    def manage_status(self, status):
        img_stream = status.picture
        something_changed = self.__motion_detector.detect_motion(img_stream)
    
        if something_changed:
            print("ALARM!!!!!")
            self.__mail_sender.send_mail(img_stream)
        else:
            print("Everything is fine")
    
        self.__uploader.upload_file_stream(img_stream, something_changed)