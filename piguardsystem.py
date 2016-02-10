from enum import Enum
from status import StatusGenerator
from actions import ActionType
from time import sleep
from messages import Message
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
            pass
        elif command == "shutdown":
            self.stop()
            self.send_message(Message.final_goodbye)
            keep_running = False
        elif command == "monitor":
            if self.mode == Mode.monitoring:
                self.send_message(Message.mode_monitoring_already_active)
            else:
                self.mode = Mode.monitoring
                self._handler_thread.mode = self.mode
                self.send_message(Message.mode_monitoring_activated)
        elif command == "surveil":
            if self.mode == Mode.surveillance:
                self.send_message(Message.mode_surveillance__already_active)
            else:
                self.mode = Mode.surveillance
                self._handler_thread.mode = self.mode
                self.send_message(Message.mode_surveillance_activated)
        elif command == "snapshot":
            self._on_demand_actions_queue.put(ActionType.uploadStatus)
            self.send_message(Message.snapshot_requested)
        elif command == "help":
            self.send_message(Message.help_command_list)
            self.send_message(Message.help_start)
            self.send_message(Message.help_stop)
            self.send_message(Message.help_monitor)
            self.send_message(Message.help_surveil)
            self.send_message(Message.help_snapshot)
            self.send_message(Message.help_shutdown)
            self.send_message(Message.help_exit)
            self.send_message(Message.help_help)
        else:
            self.send_message(Message.command_not_found)

        self.status()
        self.send_message(Message.END)
        self._messages_queue = None

        return keep_running

    def send_message(self, mess):
        if self._messages_queue is not None:
            self._messages_queue.put(mess)

    def clear_message_queue(self):
        while not self._messages_queue.empty():
            self._messages_queue.get_nowait()

    def start(self):
        self.send_message(Message.starting)
        if not self._handler_thread.is_alive():
            if self._handler_thread.is_stopped():
                self._handler_thread = StatusHandlerThread(self._statuses_queue, self._on_demand_actions_queue, self.mode)
                self.send_message(Message.status_handler_init)

            self._handler_thread.start()
            self.send_message(Message.status_handler_start)
        else:
            self.send_message(Message.status_handler_already_started)

        if not self._generator_thread.is_alive():
            if self._generator_thread.is_stopped():
                self._generator_thread = StatusGeneratorThread(self._statuses_queue)
                self.send_message(Message.status_gen_init)

            self._generator_thread.start()
            self.send_message(Message.status_gen_start)
        else:
            self.send_message(Message.status_gen_already_started)

    def stop(self):
        self.send_message(Message.stopping)
        if self._handler_thread.is_alive():
            self._handler_thread.stop()
            self._handler_thread.join()
            self.send_message(Message.status_handler_stop)

        if self._generator_thread.is_alive():
            self._generator_thread.stop()
            self._generator_thread.join()
            self.send_message(Message.status_gen_stop)
        self.send_message(Message.final_stop)

    def shutdown_servers(self):
        self._console_thread.server.shutdown()
        self.rest_service_thread.server.shutdown()

    def status(self):
        if self.system_status == System.SystemStatus.started:
            self.send_message(Message.status_started)
        else:
            self.send_message(Message.status_stopped)

        if self.mode == Mode.monitoring:
            self.send_message(Message.mode_monitoring)
        else:
            self.send_message(Message.mode_surveillance)
