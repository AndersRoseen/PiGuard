from piguardtyping import JSON, Status, Stream
from actions import IAction
import dropbox
import os
import configmanager
import storagemanager
import io
import json
import threading
import datetime


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

    def __init__(self, token: str, time_window: int):
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()
        self._dropbox = dbx
        self._time_window = time_window

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

        dbx_pictures = set(map(lambda x: x.name, self._dropbox.files_list_folder('').entries))
        dbx_pictures.discard('statuses.json')

        local_pictures = set(map(lambda x: x["picture"], statuses["statuses"]))
        local_pictures.difference_update(dbx_pictures)

        for picture_name in local_pictures:
            picture_stream = io.BytesIO()
            storagemanager.manager.write_image_on_stream(picture_name, picture_stream)
            picture_stream.seek(0)
            self.upload_file_stream(picture_stream, picture_name)

        dbx_statuses = self.get_statuses_list()
        ref_timestamp = dbx_statuses["statuses"][0]["timestamp"]
        curr_pos = 0
        for status in statuses["statuses"]:
            if status["timestamp"] == ref_timestamp:
                break
            dbx_statuses["statuses"].insert(curr_pos, status)
            curr_pos += 1

        self.clean_old_data(dbx_statuses, dbx_pictures)
        self.upload_statuses_list(dbx_statuses)

    def clean_old_data(self, statuses: JSON, pictures: set):
        now = datetime.datetime.now()
        index = 0
        for status in statuses["statuses"]:
            status_ts = datetime.datetime.strptime(status["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            if (now - status_ts).days > self._time_window:
                statuses["statuses"] = statuses["statuses"][:index]
                break
            index += 1

        pictures_to_delete = pictures.difference(set(map(lambda x: x["picture"], statuses["statuses"])))
        for picture_name in pictures_to_delete:
            self._dropbox.files_delete('/' + picture_name)

    def get_statuses_list(self) -> JSON:
        try:
            _, res = self._dropbox.files_download('/statuses.json')
            data = str(res.content, "utf-8")
            return json.loads(data)
        except dropbox.exceptions.ApiError as err:
            print('Dropbox API error: ', err)
            print('Status list file not found or impossible to download... creating a new one!')
            return {"statuses": list()}

    def perform_action(self, status: Status):
        backup_thread = threading.Thread(target=self.perform_backup)
        backup_thread.setDaemon(True)
        backup_thread.start()


def get_backup_manager():
    token = configmanager.config['dropbox']['login_token']
    time_window = configmanager.config.getint('backup', 'time_window')
    if len(token) == 0:
        token = DropboxUploader.generate_auth_token(configmanager.config['dropbox']['app_key'], configmanager.config['dropbox']['app_secret'])
        configmanager.config['dropbox']['login_token'] = token
        with open('piguard.ini', 'w') as configfile:
            configmanager.config.write(configfile)
    return DropboxUploader(token, time_window)
