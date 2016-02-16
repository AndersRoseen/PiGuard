import dropbox
import datetime
import os
import json
import storagemanager
from piguardtyping import JSON, Status, Stream
from actions import IAction


def _get_file_name(time: datetime.datetime):
        return "pic_%02d%02d%d_%02d%02d%02d.jpg" % (time.day, time.month, time.year, time.hour, time.minute, time.second)


def _prepare_json_status(status: Status) -> JSON:
    json_status = dict()

    for item in status.items():
        key, value = item
        if key == "timestamp":
            value = str(value)
        elif key == "picture":
            value = _get_file_name(status["timestamp"])

        json_status[key] = value

    return json_status


class DiskSaver(IAction):

    def perform_action(self, status: Status):
        json_status = _prepare_json_status(status)
        print("Saving status on disk!")
        storagemanager.manager.add_status(json_status)
        print("Saving picture on disk!")
        picture = status["picture"]
        storagemanager.manager.save_image(picture, json_status["picture"])


def get_data_saver():
    # token = config['dropbox']['login_token']
    # if len(token) == 0:
    #    token = DropboxUploader.generate_auth_token(config['dropbox']['app_key'], config['dropbox']['app_secret'])
    #    config['dropbox']['login_token'] = token
    #    with open('piguard.ini', 'w') as configfile:
    #        config.write(configfile)
    # return DropboxUploader(token, config.getint('general', 'data_update_interval'))
    return DiskSaver()
