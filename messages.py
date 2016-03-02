from enum import Enum


class Message(Enum):
    status_started = "PiGuard status: started"
    status_stopped = "PiGuard status: stopped"
    starting = "Starting PiGuard..."
    stopping = "Stopping PiGuard..."
    status_handler_init = "Status handler initialized!"
    status_handler_start = "Status handler started!"
    status_handler_already_started = "Status handler already started!"
    status_handler_stop = "Status handler stopped!"
    status_gen_init = "Status generator initialized!"
    status_gen_start = "Status generator started!"
    status_gen_already_started = "Status generator already started!"
    status_gen_stop = "Status generator stopped!"
    mode_surveillance = "PiGuard mode: surveillance"
    mode_monitoring = "PiGuard mode: monitoring"
    final_goodbye = "Goodbye and thank you for using PiGuard!"
    final_stop = "PiGuard successfully stopped"
    mode_monitoring_already_active = "Monitoring mode already active!"
    mode_monitoring_activated = "Monitoring mode activated!"
    mode_surveillance__already_active = "Surveillance mode already active!"
    mode_surveillance_activated = "Surveillance mode activated!"
    snapshot_requested = "Snapshot request queued!"
    command_not_found = "command not found"

    # Help messages
    help_command_list = "PiGuard available commands:"
    help_start = "\tstart: starts the processes status generator and the status handler"
    help_stop = "\tstop: stops the processes status generator and the status handler"
    help_monitor = "\tmonitor: start monitoring mode"
    help_surveil = "\tsurveil: start surveillance mode"
    help_snapshot = "\tsnapshot: upload next status!"
    help_shutdown = "\tshutdown: stops all the processes and terminates the application"
    help_exit = "\texit: terminate the console session"
    help_help = "\thelp: display this command"

    END = "END"
