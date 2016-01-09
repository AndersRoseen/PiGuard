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

    def __init__(self, shared_queue, message_queue):
        BaseQueuedThread.__init__(self, shared_queue)
        self.server = factory.get_console_server(shared_queue, message_queue)

    def run(self):
        self.server.serve_forever()
        print("Console server stopped!")


class System(object):

    def __init__(self):
        self._statuses_queue = queue.Queue()
        self._handler_thread = StatusesHandlerThread(self._statuses_queue)
        self._generator_thread = StatusesGeneratorThread(self._statuses_queue)

        self._commands_queue = queue.Queue()
        self._messages_queue = queue.Queue()
        self._console_thread = CommandConsoleThread(self._commands_queue, self._messages_queue)
        self._console_thread.start()

    def get_and_execute_command(self):
        command = self._commands_queue.get()
        return self._execute_command(command)

    def _execute_command(self, command):
        keep_running = True

        if command == "stop":
            self.stop()
        elif command == "start":
            self.start()
        elif command == "shutdown":
            self.stop()
            self.send_message("Goodbye and thank you for using PiGuard!")
            keep_running = False
        else:
            self.send_message(command + ": command not found")

        self.send_message("END")
        return keep_running
        
    def send_message(self, mess):
        self._messages_queue.put(mess)
    
    def clear_message_queue(self):
        while not self._messages_queue.empty():
            self._messages_queue.get_nowait()

    def start(self):
        self.send_message("Starting PiGuard...")
        if not self._handler_thread.is_alive():
            if self._handler_thread.is_stopped():
                self._handler_thread = StatusesHandlerThread(self._statuses_queue)
                self.send_message("Statuses' handler initialized!")

            self._handler_thread.start()
            self.send_message("Statuses' handler started!")
        else:
            self.send_message("Statuses' handler already started!")

        if not self._generator_thread.is_alive():
            if self._generator_thread.is_stopped():
                self._generator_thread = StatusesGeneratorThread(self._statuses_queue)
                self.send_message("Statuses' generator initialized!")

            self._generator_thread.start()
            self.send_message("Statuses' generator started!")
        else:
            self.send_message("Statuses' generator already started!")

    def stop(self):
        self.send_message("Stopping PiGuard...")
        self._handler_thread.stop()
        self._handler_thread.join()
        self.send_message("Statuses' handler stopped!")
        self._generator_thread.stop()
        self._generator_thread.join()
        self.send_message("Statuses' generator stopped!")
        self.send_message("PiGuard succesfuly stopped")

    def shutdown_console_server(self):
        self._console_thread.server.shutdown()


if __name__ == "__main__":

    system = System()
    system.start()
    system.clear_message_queue()
    
    while system.get_and_execute_command():
        pass

    system.shutdown_console_server()
    print("PiGuard Terminated")