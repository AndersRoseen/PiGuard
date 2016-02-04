from enum import Enum
from status import StatusGenerator
from actions import ActionType
from time import sleep
import sensors
import configmanager
import status
import console
import restservice
import threading
import queue


class Mode(Enum):
    monitoring = "monitoring"
    surveillance = "surveillance"


class BaseThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self._continue = True

    def stop(self):
        self._continue = False

    def is_stopped(self):
        return not self._continue


class StatusGeneratorThread(BaseThread):

    def __init__(self, statuses_queue):
        BaseThread.__init__(self)
        self._statuses_queue = statuses_queue
        self._generator = StatusGenerator(sensors.get_sensors())
        self._sampling_frequence = configmanager.config.getfloat('general', 'data_sampling_interval')

    def run(self):
        while self._continue:
            try:
                current_status = self._generator.get_current_status()
                self._statuses_queue.put(current_status)
                sleep(self._sampling_frequence)
            except:
                print("Unexpected error - Main")

        print("Status generator thread stopped!")


class StatusHandlerThread(BaseThread):

    def __init__(self, statuses_queue, action_queue, mode=Mode.monitoring):
        BaseThread.__init__(self)
        self.mode = mode
        self._statuses_queue = statuses_queue
        self._handler = status.get_status_handler(action_queue)
        self._sampling_frequence = configmanager.config.getfloat('general', 'data_sampling_interval')

    def run(self):
        queue_timeout = self._sampling_frequence * 3
        while self._continue:
            try:
                current_status = self._statuses_queue.get(timeout=queue_timeout)
                self._handler.manage_status(current_status, self.mode)
                self._statuses_queue.task_done()
            except queue.Empty:
                print("Status handler timeout!")
            except:
                print("Unexpected error - Worker")

        print("Status handler thread stopped!")


class CommandConsoleThread(BaseThread):

    def __init__(self, shared_queue):
        BaseThread.__init__(self)
        self.server = console.get_console_server(shared_queue)

    def run(self):
        self.server.serve_forever()
        print("Console server stopped!")


class RestServiceThread(BaseThread):

    def __init__(self, shared_queue):
        BaseThread.__init__(self)
        self.server = restservice.get_rest_server(shared_queue)

    def run(self):
        self.server.serve_forever()
        print("REST server stopped!")


class SystemActionsGenerator(threading.Thread):

    def __init__(self, actions_queue):
        super().__init__()
        self.daemon = True
        self._actions_queue = actions_queue
        self._data_update_interval = configmanager.config.getint('general', 'data_update_interval') * 60

    def run(self):
        while True:
            self._actions_queue.put(ActionType.uploadStatus)
            sleep(self._data_update_interval)


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

        actions_generator = SystemActionsGenerator(self._on_demand_actions_queue)
        actions_generator.start()

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
                self._handler_thread = StatusHandlerThread(self._statuses_queue, self._on_demand_actions_queue, self.mode)
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

    def shutdown_servers(self):
        self._console_thread.server.shutdown()
        self.rest_service_thread.server.shutdown()
