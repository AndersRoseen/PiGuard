import configparser

config = configparser.ConfigParser()
config.read('piguard.ini')
print('Config parser initialized!')