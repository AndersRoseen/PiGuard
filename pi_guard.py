from time import sleep
import queue
import threading
import factory


class BaseQueuedThread(threading.Thread):

    def __init__(self, shared_queue):
        super().__init__()
        self._queue = shared_queue
        self._continue = True

    def stop(self):
        self._continue = False

    def is_stopped(self):
        return not self._continue


class StatusesHandlerThread(BaseQueuedThread):

    def run(self):
        handler = factory.get_status_handler()
        sampling_frequence = factory.get_sampling_interval()
        queue_timeout = sampling_frequence * 3
        while self._continue:
            try:
                status = self._queue.get(timeout=queue_timeout)
                handler.manage_status(status)
                self._queue.task_done()
            except queue.Empty:
                print("Status handler timeout!")
            except:
                print("Unexpected error - Worker")

        print("Statuses handler thread stopped!")


class StatusesGeneratorThread(BaseQueuedThread):

    def run(self):
        generator = factory.get_status_generator()
        sampling_frequence = factory.get_sampling_interval()
        while self._continue:
            try:
                status = generator.get_current_status()
                self._queue.put(status)
                sleep(sampling_frequence)
            except:
                print("Unexpected error - Main")
                
        print("Statuses generator thread stopped!")


class CommandConsoleThread(BaseQueuedThread):

    def __init__(self, shared_queue):
        BaseQueuedThread.__init__(self, shared_queue)
        self.server = factory.get_console_server(shared_queue)

    def run(self):
        self.server.serve_forever()


class System(object):

    def __init__(self):
        self._statuses_queue = queue.Queue()
        self._handler_thread = StatusesHandlerThread(self._statuses_queue)
        self._generator_thread = StatusesGeneratorThread(self._statuses_queue)

        self._commands_queue = queue.Queue()
        self._console_thread = CommandConsoleThread(self._commands_queue)
        self._console_thread.start()

    def get_next_command(self):
        return self._commands_queue.get()

    def start(self):
        if not self._handler_thread.is_alive():
            if self._handler_thread.is_stopped():
                self._handler_thread = StatusesHandlerThread(self._statuses_queue)

            self._handler_thread.start()

        if not self._generator_thread.is_alive():
            if self._generator_thread.is_stopped():
                self._generator_thread = StatusesGeneratorThread(self._statuses_queue)

            self._generator_thread.start()

    def stop(self):
        self._handler_thread.stop()
        self._generator_thread.stop()

    def shutdown(self):
        self.stop()
        self._console_thread.server.shutdown()


if __name__ == "__main__":

    system = System()
    system.start()

    while True:
        command = system.get_next_command()
        if command == "stop":
            system.stop()
        elif command == "exit":
            system.shutdown()
            break
        elif command == "start":
            system.start()
    
    print("PiGuard Terminated")