import dropbox
import datetime
import os

from status import IAction, Event


def get_file_name():
        now = datetime.datetime.now()
        return "pic_%02d%02d%d_%02d%02d%02d.jpg" % (now.day, now.month, now.year, now.hour, now.minute, now.second)


class DropboxUploader(IAction):
    
    def __init__(self, token, upload_interval=1):
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        self._dropbox = dbx
        
        self._last_upload = datetime.datetime.now()
        self._upload_interval = upload_interval * 60
    
    def _upload_stream_to_dropbox(self, file_stream):
        file_name = get_file_name()
        dest_path = os.path.join('/', file_name)
        self._dropbox.files_upload(file_stream.get_stream(), dest_path, mute=True)
        
    def _should_force(self, events):
        for event in events:
            if event is Event.motionDetected:
                return True
        return False
            
    def upload_file_stream(self, file_stream, force=False):
        now = datetime.datetime.now()
        if force or (now - self._last_upload).seconds > self._upload_interval:
            self._upload_stream_to_dropbox(file_stream)
            print("Picture uploaded on Dropbox!")
            self._last_upload = now
            
    def perform_action(self, status, events):
        self.upload_file_stream(status.picture, self._should_force(events))