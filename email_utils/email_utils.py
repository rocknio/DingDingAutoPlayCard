# -*- coding: utf-8 -*-
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

__author__ = 'Neo'


def send_email(receiver, content):
    try:
        mail_host = ''
        mail_user = ''
        mail_pass = ''
        sender = ''
        receivers = [receiver]

        message = MIMEMultipart()
        message['Subject'] = content
        message['From'] = sender
        message['To'] = receivers[0]

        part = MIMEText(content, 'plain', 'utf-8')
        message.attach(part)

        # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
        with open(".\\screen_cap\\screen.png", 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('image', 'png', filename='screen.png')
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename='screen.png')
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            message.attach(mime)

        full_text = message.as_string()

        smtp_client = smtplib.SMTP()
        smtp_client.connect(mail_host, 25)
        smtp_client.login(mail_user, mail_pass)
        resp = smtp_client.sendmail(sender, receivers, full_text)
        smtp_client.quit()
        if len(resp) == 0:
            logging.info("Send Email OK")
        else:
            logging.error("Send Email Error! err = ".format(resp))
    except Exception as err:
        logging.error("Err = {}".format(err))


if __name__ == "__main__":
    send_email('1145646@qq.com', "this is a test email_utils")
