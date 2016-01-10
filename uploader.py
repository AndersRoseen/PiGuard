import dropbox
import datetime
import os
import json

from status import IAction, Event


def get_file_name(time):
        return "pic_%02d%02d%d_%02d%02d%02d.jpg" % (time.day, time.month, time.year, time.hour, time.minute, time.second)


def prepare_json_status(status, events):
    json_status = dict()
    json_status["timestamp"] = str(status.timestamp)
    json_status["picture"] = get_file_name(status.timestamp)
    json_status["events"] = list(map(str, events))
    return json_status


class DropboxUploader(IAction):

    @staticmethod
    def generate_auth_token(app_key, app_secret):
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print("2. Click \"Allow\" (you might have to log in first).")
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()

        try:
            access_token, _ = auth_flow.finish(auth_code)
            return access_token
        except Exception as e:
            print('Error: %s' % (e, ))
            return

    def __init__(self, token, upload_interval=1):
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        self._dropbox = dbx
        
        self._last_upload = datetime.datetime.now()
        self._upload_interval = upload_interval * 60
    
    def _upload_stream_to_dropbox(self, file_stream, file_name):
        dest_path = os.path.join('/', file_name)
        try:
            self._dropbox.files_upload(file_stream.get_stream(), dest_path, mute=True)
            return True
        except dropbox.exceptions.ApiError as err:
            print('Dropbox API error: ', err)
            return False
        
    def _should_force(self, events):
        for event in events:
            if event is Event.motionDetected:
                return True
        return False
            
    def upload_file_stream(self, file_stream, file_name, force=False):
        self._upload_stream_to_dropbox(file_stream, file_name)
        print("Picture uploaded on Dropbox!")

    def upload_statuses_list(self, statuses):
        mode = dropbox.files.WriteMode('overwrite', None)
        try:
            self._dropbox.files_upload(json.dumps(statuses), '/statuses.json', mode=mode)
            return True
        except dropbox.exceptions.ApiError as err:
            print('Dropbox API error: ', err)
            return False

    def upload_status(self, status, events):
        now = datetime.datetime.now()
        force = self._should_force(events)
        if force or (now - self._last_upload).seconds > self._upload_interval:
            json_status = prepare_json_status(status, events)
            statuses = self.get_statuses_list()
            statuses["statuses"].insert(0, json_status)
            success = self.upload_statuses_list(statuses)
            success = success and self.upload_file_stream(status.picture, json_status["picture"], force)
            if success:
                self._last_upload = now

    def get_statuses_list(self):
        try:
            _, res = self._dropbox.files_download('/statuses.json')
            data = str(res.content, "utf-8")
            return json.loads(data)
        except dropbox.exceptions.ApiError as err:
            print('Dropbox API error: ', err)
            print('Status list file not found or impossible to download... creating a new one!')
            return {"statuses": list()}

    def perform_action(self, status, events):
        self.upload_status(status, events)