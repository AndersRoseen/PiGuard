from time import sleep
from enum import Enum
from piguardsystem import Mode
from status import ActionType
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


class StatusHandlerThread(BaseQueuedThread):

    def __init__(self, shared_queue, action_queue, mode=Mode.monitoring):
        BaseQueuedThread.__init__(self, shared_queue)
        self.mode = mode
        self._handler = factory.get_status_handler(action_queue)
        self._sampling_frequence = factory.get_sampling_interval()

    def run(self):
        queue_timeout = self._sampling_frequence * 3
        while self._continue:
            try:
                status = self._queue.get(timeout=queue_timeout)
                self._handler.manage_status(status, self.mode)
                self._queue.task_done()
            except queue.Empty:
                print("Status handler timeout!")
            except:
                print("Unexpected error - Worker")

        print("Status handler thread stopped!")


class StatusGeneratorThread(BaseQueuedThread):

    def __init__(self, shared_queue):
        BaseQueuedThread.__init__(self, shared_queue)
        self._generator = factory.get_status_generator()
        self._sampling_frequence = factory.get_sampling_interval()

    def run(self):
        while self._continue:
            try:
                status = self._generator.get_current_status()
                self._queue.put(status)
                sleep(self._sampling_frequence)
            except:
                print("Unexpected error - Main")
                
        print("Status generator thread stopped!")


class CommandConsoleThread(BaseQueuedThread):

    def __init__(self, shared_queue):
        BaseQueuedThread.__init__(self, shared_queue)
        self.server = factory.get_console_server(shared_queue)

    def run(self):
        self.server.serve_forever()
        print("Console server stopped!")


class RestServiceThread(BaseQueuedThread):

    def __init__(self, shared_queue):
        BaseQueuedThread.__init__(self, shared_queue)
        self.server = factory.get_rest_server(shared_queue)

    def run(self):
        self.server.serve_forever()
        print("REST server stopped!")


class System(object):

    class SystemStatus(Enum):
        started = "started"
        stopped = "stopped"

    def __init__(self):
        self.system_status = System.SystemStatus.stopped
        self.mode = Mode.monitoring

        self._statuses_queue = queue.Queue()
        self._on_demand_actions_queue = queue.Queue()
        self._handler_thread = StatusHandlerThread(self._statuses_queue, self._on_demand_actions_queue, self.mode)
        self._generator_thread = StatusGeneratorThread(self._statuses_queue)

        self._commands_queue = queue.Queue()
        self._messages_queue = None
        self._console_thread = CommandConsoleThread(self._commands_queue)
        self._console_thread.start()
        self.rest_service_thread = RestServiceThread(self._commands_queue)
        self.rest_service_thread.start()

    def get_and_execute_command(self):
        command, messages_queue = self._commands_queue.get()
        return self._execute_command(command, messages_queue)

    def _execute_command(self, command, messages_queue):
        keep_running = True
        self._messages_queue = messages_queue

        if command == "stop":
            self.stop()
            self.system_status = System.SystemStatus.stopped
        elif command == "start":
            self.start()
            self.system_status = System.SystemStatus.started
        elif command == "status":
            self.send_message("PiGuard status: " + self.system_status.value)
            self.send_message("PiGuard mode: " + self.mode.value)
        elif command == "shutdown":
            self.stop()
            self.send_message("Goodbye and thank you for using PiGuard!")
            keep_running = False
        elif command == "monitor":
            if self.mode == Mode.monitoring:
                self.send_message("Monitoring mode already active!")
            else:
                self.mode = Mode.monitoring
                self._handler_thread.mode = self.mode
                self.send_message("Monitoring mode activated!")
        elif command == "surveil":
            if self.mode == Mode.surveillance:
                self.send_message("Surveillance mode already active!")
            else:
                self.mode = Mode.surveillance
                self._handler_thread.mode = self.mode
                self.send_message("Surveillance mode activated!")
        elif command == "snapshot":
            self._on_demand_actions_queue.put(ActionType.uploadStatus)
            self.send_message("Snapshot request queued!")
        elif command == "help":
            self.send_message("PiGuard available commands:")
            self.send_message("\tstart: starts the processes status generator and the status handler")
            self.send_message("\tstop: stops the processes status generator and the status handler")
            self.send_message("\tmonitor: start monitoring mode")
            self.send_message("\tsurveil: start surveillance mode")
            self.send_message("\tsnapshot: upload next status!")
            self.send_message("\tshutdown: stops all the processes and terminates the application")
            self.send_message("\texit: terminate the console session")
            self.send_message("\thelp: display this command")
        else:
            self.send_message(command + ": command not found")

        self.send_message("END")
        self._messages_queue = None

        return keep_running
        
    def send_message(self, mess):
        if self._messages_queue is not None:
            self._messages_queue.put(mess)
    
    def clear_message_queue(self):
        while not self._messages_queue.empty():
            self._messages_queue.get_nowait()

    def start(self):
        self.send_message("Starting PiGuard...")
        if not self._handler_thread.is_alive():
            if self._handler_thread.is_stopped():
                self._handler_thread = StatusHandlerThread(self._statuses_queue)
                self.send_message("Status handler initialized!")

            self._handler_thread.start()
            self.send_message("Status handler started!")
        else:
            self.send_message("Status handler already started!")

        if not self._generator_thread.is_alive():
            if self._generator_thread.is_stopped():
                self._generator_thread = StatusGeneratorThread(self._statuses_queue)
                self.send_message("Status generator initialized!")

            self._generator_thread.start()
            self.send_message("Status generator started!")
        else:
            self.send_message("Status generator already started!")

    def stop(self):
        self.send_message("Stopping PiGuard...")
        if self._handler_thread.is_alive():
            self._handler_thread.stop()
            self._handler_thread.join()
            self.send_message("Status handler stopped!")

        if self._generator_thread.is_alive():
            self._generator_thread.stop()
            self._generator_thread.join()
            self.send_message("Status generator stopped!")
        self.send_message("PiGuard successfully stopped")

    def shutdown_console_server(self):
        self._console_thread.server.shutdown()
        self.rest_service_thread.server.shutdown()


if __name__ == "__main__":

    system = System()

    while system.get_and_execute_command():
        pass

    system.shutdown_console_server()
    print("PiGuard Terminated")