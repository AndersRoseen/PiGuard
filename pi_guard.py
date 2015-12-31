from cameramanager import CameraManager
from motiondetector import MotionDetector

from time import sleep

import factory

camera_manager = CameraManager()
uploader = factory.get_uploader('piguard.ini')
mail_sender = factory.get_mail_sender('piguard.ini')
motion_detector = MotionDetector()

while True:
    img_stream = camera_manager.capture_picture()
    something_changed = motion_detector.detect_motion(img_stream)
    
    if something_changed:
        print("ALARM!!!!!")
        mail_sender.send_mail(img_stream)
    else:
        print("Everything is fine")
    
    uploader.upload_file_stream(img_stream, something_changed)
    
    sleep(2)

