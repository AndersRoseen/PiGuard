import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class MailSender:
    
    def __init__(self, user, passw, smtp_addr, smtp_port, mail_to, mail_from):
        self.__last_sent_mail_date = datetime.datetime.now()
        self.__user_id = user
        self.__pass = passw
        self.__smtp_addr = smtp_addr
        self.__smtp_port = smtp_port
        self.__to = mail_to
        self.__from = mail_from
        
    
    
    def send_mail(self, file_stream):
        now = datetime.datetime.now()
        if (now - self.__last_sent_mail_date).seconds < 60:
            return
    
        msg = MIMEMultipart()
        msg['Subject'] = "PiGuard ALERT!"
        msg['From'] = self.__from
        msg['To'] = self.__to
    
        text = MIMEText("Movement has been detected by PiGuard!")
        msg.attach(text)
        image = MIMEImage(file_stream.get_stream().read(), name="Alarm.jpg")
        msg.attach(image)
    
        s = smtplib.SMTP(self.__smtp_addr, self.__smtp_port)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.__user_id, self.__pass)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
    
        print("Warning mail sent!")
    
        self.__last_sent_mail_date = now