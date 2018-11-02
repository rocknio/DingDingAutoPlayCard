# -*- coding: utf-8 -*-
from twilio.rest import Client
import logging

__author__ = 'Neo'


def send_sms(dest_no, content):
    account_sid = ""
    auth_token = ""
    src_no = ""

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

