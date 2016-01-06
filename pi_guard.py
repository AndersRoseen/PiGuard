from time import sleep
import queue
import threading
import configparser
import factory

from status import Status, StatusHandler, StatusGenerator

def worker(statuses_queue):
    status_handler = factory.get_status_handler()
    while True:
        try:
            status = statuses_queue.get()
            status_handler.manage_status(status)
            statuses_queue.task_done()
        except:
            print("Unexpected error - Worker")


sampling_frequence = factory.get_sampling_interval()

s_queue = queue.Queue()

worker_thread = threading.Thread(target = worker, args = (s_queue, ))
worker_thread.start()

status_generator = factory.get_status_generator()
while True:
    try:
        status = status_generator.get_current_status()
        s_queue.put(status)
        sleep(sampling_frequence)
    except:
        print("Unexpected error - Main")
