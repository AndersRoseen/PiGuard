from imagestream import ImageStream
from piguardtyping import JSON, Stream
import threading
import json
import os
import datetime
import time
import configmanager


class StorageManager(object):

    def __init__(self, statuses_path: str, images_path: str, time_window: int):
        file_name = "statuses.json"
        full_path = statuses_path + file_name
        if not os.path.exists(statuses_path):
            os.makedirs(statuses_path)
        if not os.path.exists(full_path):
            statuses_list = dict()
            statuses_list["statuses"] = list()
            with open(full_path, "w") as statuses_file:
                json.dump(statuses_list, statuses_file)
        if not os.path.exists(images_path):
            os.makedirs(images_path)

        self.file_path = full_path
        self.pictures_dir = images_path
        self._semaphore = threading.BoundedSemaphore()
        self._last_update = datetime.datetime.now()
        self._time_window = time_window

    def add_status(self, status: JSON):
        with self._semaphore:
            statuses = self._unsafe_get_statuses()
            statuses["statuses"].insert(0, status)
            self._unsafe_save_statuses(statuses)

    def get_statuses(self) -> JSON:
        with self._semaphore:
            return self._unsafe_get_statuses()

    def _unsafe_get_statuses(self) -> JSON:
        statuses_file = open(self.file_path, "r")
        statuses_list = json.load(statuses_file)
        statuses_file.close()
        return statuses_list

    def write_statuses_on_stream(self, stream: Stream, time_frame: int = 0):
        if time_frame != 0:
            ref_date = datetime.datetime.now() - datetime.timedelta(hours=time_frame)
            statuses = self.get_statuses_till_date(ref_date)
            json.dump(statuses, stream)
        else:
            with self._semaphore:
                with open(self.file_path, "rb") as statuses_file:
                    stream.write(statuses_file.read())

    def _get_statuses_till_date(self, date: datetime.datetime):
        statuses = self.get_statuses()
        for index, status in enumerate(statuses["statuses"]):
            status_timestamp = datetime.datetime.strptime(status["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            if status_timestamp <= date:
                statuses["statuses"] = statuses["statuses"][:index]
                break
        return statuses

    def save_statuses(self, statuses: JSON):
        with self._semaphore:
            self._unsafe_save_statuses(statuses)

    def _unsafe_save_statuses(self, statuses: JSON):
        with open(self.file_path, "w") as statuses_file:
            json.dump(statuses, statuses_file)
            self._last_update = datetime.datetime.now()

    def clean_up_old_statuses(self):
        print("Starting clean up...")
        statuses = self.get_statuses()
        current_date = datetime.datetime.now()

        delete_index = len(statuses["statuses"])
        for i, status in enumerate(statuses["statuses"]):
            status_timestamp = datetime.datetime.strptime(status["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            if (current_date - status_timestamp).days >= self._time_window:
                delete_index = i
                break

        for status in statuses["statuses"][delete_index:]:
            image_path = self.pictures_dir + status["picture"]
            os.remove(image_path)
            print("Status and picture removed!")

        statuses["statuses"] = statuses["statuses"][:delete_index]
        if self._last_update > current_date:
            with self._semaphore:
                new_statuses = self._unsafe_get_statuses()
                for i, status in enumerate(new_statuses["statuses"]):
                    status_timestamp = datetime.datetime.strptime(status["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                    if status_timestamp > current_date:
                        statuses.insert(i, status)
                    else:
                        break
                self._unsafe_save_statuses(statuses)
        else:
            self.save_statuses(statuses)

    def save_image(self, image_stream: ImageStream, image_name: str):
        image_stream.get_image().save(self.pictures_dir + image_name)

    def write_image_on_stream(self, image_name: str, stream: Stream):
        with open(self.pictures_dir + image_name, 'rb') as image_file:
            stream.write(image_file.read())


manager = StorageManager(configmanager.config["storage"]["statuses_location"],
                         configmanager.config["storage"]["images_location"],
                         configmanager.config.getint('storage', 'time_window'))


def _clean_up_operation():
    global manager
    while True:
        manager.clean_up_old_statuses()
        time.sleep(7200)

_cleaning_thread = threading.Thread(target=_clean_up_operation)
_cleaning_thread.setDaemon(True)
_cleaning_thread.start()
