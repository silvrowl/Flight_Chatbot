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
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

class cust_input(object):
    def __init__(self, cnt, cnt_return, cnt_money, no_bud, one_way, text, Locations_list, Locations_type, Dates_list, Money_list, response):
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
        
with open('./pkl_files/p1.pkl', 'wb') as output:
    p1 = cust_input(0,0,0,False,False,'',[],[],[],[],'')   
    pickle.dump(p1, output, pickle.HIGHEST_PROTOCOL)

@slack_events_adapter.on("message")
def message(payload):             
    """endpoint for receiving all slash command requests from Slack"""

    # get the full request from Slack
    #slack_request = request.form

    # starting a new thread for doing the actual processing    
    x = threading.Thread(
            target=some_processing,
            args=(payload,)
        )
    x.start()

    ## respond to Slack with quick message
    # and end the main thread for this request
    return "Processing information.... please wait"

def some_processing(payload):
    """function for doing the actual work in a thread"""

    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    
    print(user_id)
   
    if user_id != 'U011H6XDGM8':
        
        #slack_web_client.chat_postMessage(channel=channel_id,text='processing...')
        
        with open('./pkl_files/p1.pkl', 'rb') as input:
            p1 = pickle.load(input)
        
        p1.text = event.get("text")
        
        if p1.text == 'restart':
            p1 = cust_input(0,0,0,False,False,'',[],[],[],[],'')   

        #print(p1)
        
        p1 = cbr.bot_response(p1)
        
        #print(p1)
        
        cust_output = str(p1.response)
        
        if cust_output != event.get("text"):
            slack_web_client.chat_postMessage(channel=channel_id,text=cust_output)
    
        with open('./pkl_files/p1.pkl', 'wb') as output:
            #p1 = cust_input(0,0,0,False,False,'',[],[],[],[],'')   
            pickle.dump(p1, output, pickle.HIGHEST_PROTOCOL)
        
    return 'message given'


if __name__ == "__main__":
    #logger = logging.getLogger()
    #logger.setLevel(logging.DEBUG)
    #logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=3000)