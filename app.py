#!/usr/bin/env python
# coding: utf-8

# Script to run the slackbot for travel flights

# All Imports
import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
import ssl as ssl_lib
import certifi
import pickle
import chat_bot_response as cbr
import threading
from time import sleep
from flask import Flask, json, request
import requests

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app
)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize customer class
class Cust_Input(object):
    def __init__(
        self,
        cnt,
        cnt_return,
        cnt_money,
        no_bud,
        one_way,
        text,
        Locations_list,
        Locations_type,
        Dates_list,
        Money_list,
        response,
    ):
        self.cnt = cnt
        self.cnt_return = cnt_return
        self.cnt_money = cnt_money
        self.no_bud = no_bud
        self.one_way = one_way
        self.text = text
        self.Locations_list = Locations_list
        self.Locations_type = Locations_type
        self.Dates_list = Dates_list
        self.Money_list = Money_list
        self.response = response


# Open pickle file for customer class
with open("./pkl_files/p1.pkl", "wb") as output:
    p1 = Cust_Input(0, 0, 0, False, False, "", [], [], [], ["500"], "")
    pickle.dump(p1, output, pickle.HIGHEST_PROTOCOL)

output.close()

# Message events handler
@slack_events_adapter.on("message")
def message(payload):

    # starting a new thread for doing the actual processing
    x = threading.Thread(target=some_processing, args=(payload,))
    x.start()

    # Respond to Slack with quick message and end the main thread for this request
    return "Processing information.... please wait"


def some_processing(payload):

    # Get the message payload
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")

    # Print message ID
    print(user_id)

    # Make sure response is not from the bot
    if user_id != "U011H6XDGM8":

        with open("./pkl_files/p1.pkl", "rb") as input:
            p1 = pickle.load(input)
        input.close()

        # Get the paylod text
        p1.text = event.get("text")

        # Clear the class if told to restart
        if p1.text == "restart":
            p1 = Cust_Input(0, 0, 0, False, False, "", [], [], [], ["500"], "")

        # Get the reponse from the bot
        p1 = cbr.bot_response(p1)
        cust_output = str(p1.response)

        # Output bot response to slack
        if cust_output != event.get("text"):
            slack_web_client.chat_postMessage(channel=channel_id, text=cust_output)

        # Save response to pickle file
        with open("./pkl_files/p1.pkl", "wb") as output:
            pickle.dump(p1, output, pickle.HIGHEST_PROTOCOL)

        output.close()

        # Add conversation into custom list
        with open("./pkl_files/custom_list.pkl", "rb") as f:
            custom_list = pickle.load(f)
        f.close()

        # Append new converstion to file
        custom_list.append([event.get("text")])
        custom_list.append([cust_output])

        # Save the new file
        with open("./pkl_files/custom_list.pkl", "wb") as f:
            pickle.dump(custom_list, f)
        f.close()

    return "message given"


if __name__ == "__main__":
    # logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    # logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=3000)
