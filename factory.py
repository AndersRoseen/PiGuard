import configparser
from uploader import PictureUploader
from mailsender import MailSender
from cameramanager import CameraManager
from motiondetector import MotionDetector

config = configparser.ConfigParser()
config.read('piguard.ini')
print('Config parser initialized!')
    
def get_sampling_interval():
    global config
    return config.getfloat('general','data_sampling_interval')

def get_uploader():
    global config
    return PictureUploader(config['dropbox']['token'], config.getint('general','data_update_interval'))

def get_mail_sender():
    global config
    user = config['mail']['user_id']
    passw = config['mail']['pass']
    server = config['mail']['smtp_server']
    port = config['mail']['smtp_port']
    mfrom = config['mail']['from']
    mto = config['mail']['to']

    return MailSender(user, passw, server, port, mfrom, mto)
    
def get_camera_manager():
    return CameraManager()
    
def get_motion_detector():
    return MotionDetector()
    
def get_sensors():
    sensors = []
    sensors.append(get_camera_manager())
    return sensors