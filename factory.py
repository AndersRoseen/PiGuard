import configparser
from uploader import DropboxUploader, DiskSaver
from mailsender import MailSender
from camerasensor import CameraSensor
from motiondetector import MotionDetector
from status import Event, ActionType, StatusHandler, StatusGenerator
from console import ConsoleServer, CommandHandler
from restservice import RestServer, RestRequestHandler
from authmanager import AuthManager
import os
import base64

config = configparser.ConfigParser()
config.read('piguard.ini')
print('Config parser initialized!')


def get_sampling_interval():
    global config
    return config.getfloat('general','data_sampling_interval')


def get_uploader():
    global config
    # token = config['dropbox']['login_token']
    # if len(token) == 0:
    #    token = DropboxUploader.generate_auth_token(config['dropbox']['app_key'], config['dropbox']['app_secret'])
    #    config['dropbox']['login_token'] = token
    #    with open('piguard.ini', 'w') as configfile:
    #        config.write(configfile)
    # return DropboxUploader(token, config.getint('general', 'data_update_interval'))
    return DiskSaver(config.getint('general', 'data_update_interval'))


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
    sensors = list()
    sensors.append(get_camera_sensor())
    return sensors


def get_status_analyzers():
    analyzers = list()
    analyzers.append(get_motion_detector())
    return analyzers


def get_actions():
    actions = dict()
    actions[ActionType.sendMail] = get_mail_sender()
    actions[ActionType.uploadStatus] = get_uploader()
    return actions


def get_actions_per_event():
    ea = dict()
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


def get_ip_address():
    f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d " " -f1')
    ip = f.read()
    return ip


def get_console_server(commands_queue):
    HOST, PORT = get_ip_address(), 2727
    return ConsoleServer((HOST, PORT), CommandHandler, commands_queue)


def get_auth_manager():
    credentials = set()
    list_cred = config["auth"]["credentials"].split(",")
    for cred in list_cred:
        credentials.add(str(base64.b64encode(bytes(cred, "utf-8")), "utf-8"))

    return AuthManager(credentials)


def get_rest_server(commands_queue):
    certificate_path = config["rest_service"]["server_certificate_location"]
    HOST, PORT = get_ip_address(), 2728
    return RestServer((HOST, PORT), RestRequestHandler, commands_queue, get_auth_manager(), certificate_path)
