import configparser
from uploader import DropboxUploader
from mailsender import MailSender
from camerasensor import CameraSensor
from motiondetector import MotionDetector
from status import Event, ActionType, StatusHandler, StatusGenerator
from console import ConsoleServer, CommandHandler

config = configparser.ConfigParser()
config.read('piguard.ini')
print('Config parser initialized!')
    
def get_sampling_interval():
    global config
    return config.getfloat('general','data_sampling_interval')

def get_uploader():
    global config
    return DropboxUploader(config['dropbox']['token'], config.getint('general','data_update_interval'))

def get_mail_sender():
    global config
    user = config['mail']['user_id']
    passw = config['mail']['pass']
    server = config['mail']['smtp_server']
    port = config['mail']['smtp_port']
    mfrom = config['mail']['from']
    mto = config['mail']['to']

    return MailSender(user, passw, server, port, mfrom, mto)
    
def get_camera_sensor():
    return CameraSensor()
    
def get_motion_detector():
    return MotionDetector()
    
def get_sensors():
    sensors = []
    sensors.append(get_camera_sensor())
    return sensors
    
def get_status_analyzers():
    analyzers = []
    analyzers.append(get_motion_detector())
    return analyzers
    
def get_actions():
    actions = {}
    actions[ActionType.sendMail] = get_mail_sender()
    actions[ActionType.uploadStatus] = get_uploader()
    
    return actions
    
def get_actions_per_event():
    ea = {}
    ea[Event.empty] = [ActionType.uploadStatus]
    ea[Event.motionDetected] = [ActionType.sendMail, ActionType.uploadStatus]
    return ea
    
def get_status_handler():
    analyzers = get_status_analyzers()
    actions = get_actions()
    actions_per_event = get_actions_per_event()
    
    return StatusHandler(analyzers, actions, actions_per_event)
    
def get_status_generator():
    sensors = get_sensors()
    return StatusGenerator(sensors)

def get_console_server(commands_queue):
    HOST, PORT = "localhost", 9999
    return ConsoleServer((HOST, PORT), CommandHandler, commands_queue)