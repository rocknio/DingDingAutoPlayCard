# -*- coding: utf-8 -*-
from twilio.rest import Client
import logging

__author__ = 'Neo'


def send_sms(dest_no, content):
    account_sid = "twilio account id"
    auth_token = "twilio auth token"

    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            to=dest_no,
            from_="twilio sms number",
            body=content
        )

        logging.info("send sms OK,msgid = {}".format(message.sid))
    except Exception as err:
        logging.error("err = {}".format(err))

