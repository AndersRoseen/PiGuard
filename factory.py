from uploader import DropboxUploader, DiskSaver
from mailsender import MailSender
from motiondetector import MotionDetector
from status import Event, ActionType, StatusHandler, StatusGenerator
from console import ConsoleServer, CommandHandler
from restservice import RestServer, RestRequestHandler
from piguardsystem import Mode
import os
import configmanager
import sensors


def get_sampling_interval():
    return configmanager.config.getfloat('general', 'data_sampling_interval')


def get_uploader():
    global config
    # token = config['dropbox']['login_token']
    # if len(token) == 0:
    #    token = DropboxUploader.generate_auth_token(config['dropbox']['app_key'], config['dropbox']['app_secret'])
    #    config['dropbox']['login_token'] = token
    #    with open('piguard.ini', 'w') as configfile:
    #        config.write(configfile)
    # return DropboxUploader(token, config.getint('general', 'data_update_interval'))
    return DiskSaver(configmanager.config.getint('general', 'data_update_interval'))


def get_mail_sender():
    user = configmanager.config['mail']['user_id']
    passw = configmanager.config['mail']['pass']
    server = configmanager.config['mail']['smtp_server']
    port = configmanager.config['mail']['smtp_port']
    mfrom = configmanager.config['mail']['from']
    mto = configmanager.config['mail']['to']
    return MailSender(user, passw, server, port, mfrom, mto)


def get_motion_detector():
    return MotionDetector()


def get_sensors():
    sensors_list = list()

    sensors_to_use = configmanager.config["sensors"]["sensors_list"].split(",")
    generators = sensors.get_sensor_generators()
    for sensor in sensors_to_use:
        sensors_list.append(generators[sensor]())

    return sensors_list


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
    ea[Mode.surveillance] = dict()
    ea[Mode.surveillance][Event.empty] = [ActionType.uploadStatus]
    ea[Mode.surveillance][Event.motionDetected] = [ActionType.sendMail, ActionType.uploadStatus]

    ea[Mode.monitoring] = dict()
    ea[Mode.monitoring][Event.empty] = [ActionType.uploadStatus]
    ea[Mode.monitoring][Event.motionDetected] = list()

    return ea


def get_status_handler(action_queue):
    analyzers = get_status_analyzers()
    actions = get_actions()
    actions_per_event = get_actions_per_event()
    
    return StatusHandler(analyzers, actions, actions_per_event, action_queue)


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


def get_rest_server(commands_queue):
    certificate_path = configmanager.config["rest_service"]["server_certificate_location"]
    key_path = configmanager.config["rest_service"]["server_key_location"]
    HOST, PORT = get_ip_address(), 2728
    return RestServer((HOST, PORT), RestRequestHandler, commands_queue, key_path, certificate_path)
