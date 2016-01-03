import dropbox
import datetime
import os

from status import IAction, Event

class PictureUploader(IAction):
    
    def __init__(self, token, upload_interval=1):
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        self.__dropbox = dbx
        
        self.__last_upload = datetime.datetime.now()
        self.__upload_interval = upload_interval * 60
        
    def __get_file_name(self):
        now = datetime.datetime.now()
        return "pic_%02d%02d%d_%02d%02d%02d.jpg" % (now.day,now.month, now.year, now.hour, now.minute, now.second)
    
    def __upload_stream_to_dropbox(self, file_stream):
        file_name = self.__get_file_name()
        dest_path = os.path.join('/', file_name)
        self.__dropbox.files_upload(file_stream.get_stream(), dest_path, mute=True)
        
    def __should_force(self, events):
        for event in events:
            if event is Event.motionDetected:
                return True
        return False
            
    def upload_file_stream(self, file_stream, force=False):
        now = datetime.datetime.now()
        if force or (now - self.__last_upload).seconds > self.__upload_interval:
            self.__upload_stream_to_dropbox(file_stream)
            print("Picture uploaded on Dropbox!")
            self.__last_upload = now
            
    def perform_action(self, status, events):
        self.upload_file_stream(status.picture, self.__should_force(events))