"""
Mailsender is an action that send an alert in case of detected motion with a picture of the room as attachment
"""
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import datetime
import smtplib
from imagestream import ImageStream
import configmanager
from actions import IAction
from piguardtyping import Status


class MailSender(IAction):

    def __init__(self, user: str, passw: str, smtp_addr: str, smtp_port: str, mail_to: str, mail_from: str):
        self._last_sent_mail_date = datetime.datetime.now()
        self._user_id = user
        self._pass = passw
        self._smtp_addr = smtp_addr
        self._smtp_port = smtp_port
        self._to = mail_to
        self._from = mail_from

    def _send_mail(self, file_stream: ImageStream):
        now = datetime.datetime.now()
        if (now - self._last_sent_mail_date).seconds < 120:
            return

        msg = MIMEMultipart()
        msg['Subject'] = "PiGuard ALERT!"
        msg['From'] = self._from
        msg['To'] = self._to

        text = MIMEText("Movement has been detected by PiGuard!")
        msg.attach(text)
        image = MIMEImage(file_stream.get_stream().read(), name="Alarm.jpg")
        msg.attach(image)

        smtp_server = smtplib.SMTP(self._smtp_addr, self._smtp_port)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.ehlo()
        smtp_server.login(self._user_id, self._pass)
        smtp_server.sendmail(msg['From'], msg['To'], msg.as_string())
        smtp_server.quit()

        print("Warning mail sent!")

        self._last_sent_mail_date = now

    def perform_action(self, status: Status):
        picture = status["picture"]
        self._send_mail(picture)


def get_mail_sender() -> MailSender:
    user = configmanager.config['mail']['user_id']
    passw = configmanager.config['mail']['pass']
    server = configmanager.config['mail']['smtp_server']
    port = configmanager.config['mail']['smtp_port']
    mfrom = configmanager.config['mail']['from']
    mto = configmanager.config['mail']['to']
    return MailSender(user, passw, server, port, mto, mfrom)
