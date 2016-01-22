import threading
import json
import os
import datetime


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
        self._last_update = datetime.datetime.now()

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

    def _clean_up_old_statuses(self):
        statuses = self.get_statuses()
        current_date = datetime.datetime.now()

        delete_index = len(statuses["statuses"])
        for i, status in enumerate(statuses["statuses"]):
            status_timestamp = datetime.datetime.strptime(status["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            if (current_date - status_timestamp).days > 2:
                delete_index = i
                break

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


storage = StatusesStorage()
