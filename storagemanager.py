import threading
import json
import os
import datetime
import time


class StorageManager(object):

    def __init__(self):
        path = "/home/pi/Documents/PiGuardData/"
        file_name = "statuses.json"
        full_path = path + file_name
        pic_dir = "/home/pi/Pictures/PiGuard/"
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(full_path):
            statuses_list = dict()
            statuses_list["statuses"] = list()
            with open(full_path, "w") as statuses_file:
                json.dump(statuses_list, statuses_file)
        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)

        self.file_path = full_path
        self.pictures_dir = pic_dir
        self._semaphore = threading.BoundedSemaphore()
        self._last_update = datetime.datetime.now()

    def add_status(self, status):
        with self._semaphore:
            statuses = self._unsafe_get_statuses()
            statuses["statuses"].insert(0, status)
            self._unsafe_save_statuses(statuses)

    def get_statuses(self):
        with self._semaphore:
            return self._unsafe_get_statuses()

    def _unsafe_get_statuses(self):
        statuses_file = open(self.file_path, "r")
        statuses_list = json.load(statuses_file)
        statuses_file.close()
        return statuses_list

    def write_statuses_on_stream(self, stream):
        with self._semaphore:
            with open(self.file_path, "rb") as statuses_file:
                stream.write(statuses_file.read())

    def save_statuses(self, statuses):
        with self._semaphore:
            self._unsafe_save_statuses(statuses)

    def _unsafe_save_statuses(self, statuses):
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
            if (current_date - status_timestamp).days > 2:
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

    def save_image(self, image_stream, image_name):
        image_stream.get_image().save(self.pictures_dir + image_name)

    def write_image_on_stream(self, image_name, stream):
        with open(self.pictures_dir + image_name, 'rb') as image_file:
            stream.write(image_file.read())


manager = StorageManager()


def _clean_up_operation():
    global manager
    while True:
        manager.clean_up_old_statuses()
        time.sleep(7200)

_cleaning_thread = threading.Thread(target=_clean_up_operation)
_cleaning_thread.setDaemon(True)
_cleaning_thread.start()
