# -*- coding: utf-8 -*-
from twilio.rest import Client
import logging

__author__ = 'Neo'


def send_sms(dest_no, content):
    account_sid = "AC0116268004c721182cbd674ccda2e332"
    auth_token = "ec04d5aaa2aaa5b2e9bad54a016911d5"
    src_no = "+13163336152"

    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            to=dest_no,
            from_=src_no,
            body=content
        )

        logging.info("send sms OK,msgid = {}".format(message.sid))
    except Exception as err:
        logging.error("err = {}".format(err))
