from abc import ABCMeta, abstractmethod
import datetime
import factory

class Status:
    
    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.picture = None

class Analysis:
    
    def __init__(self):
        self.motion_detected = False
        self.current_image = None
        


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
        self.__analyzers = factory.get_status_analyzers()
        
        self.__uploader = factory.get_uploader()
        self.__mail_sender = factory.get_mail_sender()
        
        
    def manage_status(self, status):
        analysis = self.__analyze(status)
        #instead of an analysis a list of events is returned
        #each event has an array of handler associated
    
        if analysis.motion_detected:
            print("ALARM!!!!!")
            self.__mail_sender.send_mail(img_stream)
        else:
            print("Everything is fine")
    
        self.__uploader.upload_file_stream(img_stream, something_changed)
    
    def __analyze(self, status):
        analysis = Analysis()
        for analyzer in self.__analyzers:
            analyzer.analyze_status(status, analysis)
            
        return analysis
        

class IStatusAnalyzer(metaclass=ABCMeta):
    
    @abstractmethod
    def analyze_status(self, status, analysis):
        pass