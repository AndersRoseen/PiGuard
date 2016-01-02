from time import sleep
import queue
import threading
import configparser
import factory

from status import Status, StatusHandler, StatusGenerator

def worker(statuses_queue):
    status_handler = StatusHandler()
    while True:
        status = statuses_queue.get()
        status_handler.manage_status(status)
        statuses_queue.task_done()


sampling_frequence = factory.get_sampling_interval()

s_queue = queue.Queue()

worker_thread = threading.Thread(target = worker, args = (s_queue, ))
worker_thread.start()

status_generator = StatusGenerator()
while True:
    status = status_generator.get_current_status()
    s_queue.put(status)
    sleep(sampling_frequence)
