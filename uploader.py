import dropbox
import datetime
import os

class PictureUploader:
    
    def __init__(self, token):
        dbx = dropbox.Dropbox(token)
        #dbx = dropbox.Dropbox("aK3f3Rqc4uMAAAAAAAAAq2rMlgPXsJgg_54RMv4_2Qr7XMt-jvefA7VP-z38CSHC")
        dbx.users_get_current_account()
        self.__dropbox = dbx
        
        self.__last_upload = datetime.datetime.now()
        
    def __get_file_name(self):
        now = datetime.datetime.now()
        return "pic_%02d%02d%d_%02d%02d%02d.jpg" % (now.day,now.month, now.year, now.hour, now.minute, now.second)
    
    def __upload_stream_to_dropbox(self, file_stream):
        file_name = self.__get_file_name()
        dest_path = os.path.join('/', file_name)
        self.__dropbox.files_upload(file_stream.get_stream(), dest_path, mute=True)
            
    def upload_file_stream(self, file_stream, is_alarm):
        now = datetime.datetime.now()
        if is_alarm or (now - self.__last_upload).seconds > 60:
            self.__upload_stream_to_dropbox(file_stream)
            print("Picture uploaded on Dropbox!")
            self.__last_upload = now