import configparser
from uploader import PictureUploader
from mailsender import MailSender

def get_uploader(config_file_name):
    config = configparser.ConfigParser()
    config.read(config_file_name)
    return PictureUploader(config['dropbox']['token'])
    
def get_mail_sender(config_file_name):
    config = configparser.ConfigParser()
    config.read(config_file_name)
    
    user = config['mail']['user_id']
    passw = config['mail']['pass']
    server = config['mail']['smtp_server']
    port = config['mail']['smtp_port']
    mfrom = config['mail']['from']
    mto = config['mail']['to']
    
    return MailSender(user, passw, server, port, mfrom, mto)