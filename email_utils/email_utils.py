# -*- coding: utf-8 -*-
import smtplib
import logging
from email.mime.text import MIMEText

__author__ = 'Neo'


def send_email(receiver, content):
    try:
        mail_host = 'smtp.163.com'
        mail_user = 'rocknio'
        mail_pass = 'songyn28'
        sender = 'rocknio@163.com'
        receivers = [receiver]

        message = MIMEText('content', 'plain', 'utf-8')
        message['Subject'] = content
        message['From'] = sender
        message['To'] = receivers[0]

        smtp_client = smtplib.SMTP()
        smtp_client.connect(mail_host, 25)
        smtp_client.login(mail_user, mail_pass)
        resp = smtp_client.sendmail(sender, receivers, message.as_string())
        smtp_client.quit()
        logging.info("Send Email = {}".format(resp))
    except Exception as err:
        logging.error("Err = {}".format(err))


if __name__ == "__main__":
    send_email('1145646@qq.com', "this is a test email_utils")
