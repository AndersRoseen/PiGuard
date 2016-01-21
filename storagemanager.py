import threading
import json
import os


class StatusesStorage(object):

    def __init__(self):
        path = "/home/pi/Documents/PiGuardData/"
        file_name = "statuses.json"
        full_path = path + file_name
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(full_path):
            statuses_list = dict()
            statuses_list["statuses"] = list()
            with open(full_path, "w") as statuses_file:
                json.dump(statuses_list, statuses_file)

        self.file_path = full_path
        self._semaphore = threading.BoundedSemaphore()

    def get_statuses(self):
        with self._semaphore:
            statuses_file = open(self.file_path, "r")
            statuses_list = json.load(statuses_file)
            statuses_file.close()
            return statuses_list

    def save_statuses(self, statuses):
        with self._semaphore:
            with open(self.file_path, "w") as statuses_file:
                json.dump(statuses, statuses_file)

storage = StatusesStorage()
