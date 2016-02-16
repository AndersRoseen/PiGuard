from piguardtyping import JSON, Status, Stream
from actions import IAction
import dropbox
import os
import configmanager
import storagemanager
import io
import json
import threading


class DropboxUploader(IAction):

    @staticmethod
    def generate_auth_token(app_key: str, app_secret: str):
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

    def __init__(self, token: str):
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        self._dropbox = dbx

    def _upload_stream_to_dropbox(self, file_stream: Stream, file_name: str) -> bool:
        dest_path = os.path.join('/', file_name)
        try:
            self._dropbox.files_upload(file_stream, dest_path, mute=True)
            return True
        except dropbox.exceptions.ApiError as err:
            print('Dropbox API error: ', err)
            return False

    def upload_file_stream(self, file_stream: Stream, file_name: str) -> bool:
        result = self._upload_stream_to_dropbox(file_stream, file_name)
        print("Picture uploaded on Dropbox!")
        return result

    def upload_statuses_list(self, statuses: JSON) -> bool:
        mode = dropbox.files.WriteMode('overwrite', None)
        try:
            self._dropbox.files_upload(json.dumps(statuses), '/statuses.json', mode=mode)
            return True
        except dropbox.exceptions.ApiError as err:
            print('Dropbox API error: ', err)
            return False

    def perform_backup(self):
        statuses = storagemanager.manager.get_statuses()
        self.upload_statuses_list(statuses)
        for status in statuses["statuses"]:
            picture_name = status["picture"]
            picture_stream = io.BytesIO()
            storagemanager.manager.write_image_on_stream(picture_name, picture_stream)
            picture_stream.seek(0)
            self.upload_file_stream(picture_stream, picture_name)

    def perform_action(self, status: Status):
        backup_thread = threading.Thread(target=self.perform_backup)
        backup_thread.setDaemon(True)
        backup_thread.start()


def get_backup_manager():
    token = configmanager.config['dropbox']['login_token']
    if len(token) == 0:
        token = DropboxUploader.generate_auth_token(configmanager.config['dropbox']['app_key'], configmanager.config['dropbox']['app_secret'])
        configmanager.config['dropbox']['login_token'] = token
        with open('piguard.ini', 'w') as configfile:
            configmanager.config.write(configfile)
    return DropboxUploader(token)
