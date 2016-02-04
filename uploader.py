import dropbox
import datetime
import os
import json
import storagemanager
import configmanager

from actions import IAction, Event


def _get_file_name(time):
        return "pic_%02d%02d%d_%02d%02d%02d.jpg" % (time.day, time.month, time.year, time.hour, time.minute, time.second)


def _prepare_json_status(status, events):
    json_status = dict()

    for item in status.items():
        key, value = item
        if key == "timestamp":
            value = str(value)
        elif key == "picture":
            value = _get_file_name(status["timestamp"])

        json_status[key] = value

    json_status["events"] = list(map(str, events))
    return json_status


def _should_force(events):
    for event in events:
        if event is Event.motionDetected or event is Event.onDemandRequest:
            return True
    return False


class DropboxUploader(IAction):

    @staticmethod
    def generate_auth_token(app_key, app_secret):
        auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

        authorize_url = auth_flow.start()
        print("This is the first time you use PiGuard with Dropbox,")
        print("to give PiGuard access to your Dropbox folder do the following:")
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
            
    def upload_file_stream(self, file_stream, file_name, force=False):
        result = self._upload_stream_to_dropbox(file_stream, file_name)
        print("Picture uploaded on Dropbox!")
        return result

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
        force = _should_force(events)
        if force or (now - self._last_upload).seconds > self._upload_interval:
            json_status = _prepare_json_status(status, events)
            statuses = self.get_statuses_list()
            statuses["statuses"].insert(0, json_status)
            success = self.upload_statuses_list(statuses)
            picture = status["picture"]
            success = success and self.upload_file_stream(picture, json_status["picture"], force)
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


class DiskSaver(IAction):

    def __init__(self, upload_interval=1):
        self._last_upload = datetime.datetime.now()
        self._upload_interval = upload_interval * 60

    def perform_action(self, status, events):
        now = datetime.datetime.now()
        force = _should_force(events)
        if force or (now - self._last_upload).seconds > self._upload_interval:
            json_status = _prepare_json_status(status, events)
            print("Saving status on disk!")
            storagemanager.manager.add_status(json_status)
            print("Saving picture on disk!")
            picture = status["picture"]
            storagemanager.manager.save_image(picture, json_status["picture"])
            self._last_upload = now


def get_uploader():
    global config
    # token = config['dropbox']['login_token']
    # if len(token) == 0:
    #    token = DropboxUploader.generate_auth_token(config['dropbox']['app_key'], config['dropbox']['app_secret'])
    #    config['dropbox']['login_token'] = token
    #    with open('piguard.ini', 'w') as configfile:
    #        config.write(configfile)
    # return DropboxUploader(token, config.getint('general', 'data_update_interval'))
    return DiskSaver(configmanager.config.getint('general', 'data_update_interval'))