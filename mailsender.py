import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from status import IAction

class MailSender(IAction):
    
    def __init__(self, user, passw, smtp_addr, smtp_port, mail_to, mail_from):
        self._last_sent_mail_date = datetime.datetime.now()
        self._user_id = user
        self._pass = passw
        self._smtp_addr = smtp_addr
        self._smtp_port = smtp_port
        self._to = mail_to
        self._from = mail_from
        
    
    
    def _send_mail(self, file_stream):
        now = datetime.datetime.now()
        if (now - self._last_sent_mail_date).seconds < 60:
            return
    
        msg = MIMEMultipart()
        msg['Subject'] = "PiGuard ALERT!"
        msg['From'] = self._from
        msg['To'] = self._to
    
        text = MIMEText("Movement has been detected by PiGuard!")
        msg.attach(text)
        image = MIMEImage(file_stream.get_stream().read(), name="Alarm.jpg")
        msg.attach(image)
    
        s = smtplib.SMTP(self._smtp_addr, self._smtp_port)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self._user_id, self._pass)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()
    
        print("Warning mail sent!")
    
        self._last_sent_mail_date = now
        
        
    def perform_action(self, status, events):
        self._send_mail(status.picture)