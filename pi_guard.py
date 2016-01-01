from cameramanager import CameraManager
from time import sleep
import queue
import threading

from status import Status, StatusHandler

def worker(statuses_queue):
    status_handler = StatusHandler()
    while True:
        status = statuses_queue.get()
        status_handler.manage_status(status)
        statuses_queue.task_done()
        
camera_manager = CameraManager()
s_queue = queue.Queue()
worker_thread = threading.Thread(target = worker, args = (s_queue, ))
worker_thread.start()

while True:
    img_stream = camera_manager.capture_picture()
    status = Status(img_stream)
    s_queue.put(status)
    sleep(2)
