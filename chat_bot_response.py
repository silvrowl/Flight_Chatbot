#!/usr/bin/env python
# coding: utf-8

# Script to compute the chat bot response to user input

# All Imports
#%pip install chatterbot-corpus -qq
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import ner_algorithm as ner
import pickle
import pandas as pd
import api_request_parse as rp
from constants import DATABASE_URI

# Initialize chatbot
bot = ChatBot(
    "TravelJohnny",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri="sqlite:///database.sqlite3",
)

# Open file containing training data and new conversations
with open("./pkl_files/custom_list.pkl", "rb") as f:
    custom_list = pickle.load(f)

custom_list_2 = []

# Shape for usage in bot trainer
for s in custom_list:
    custom_list_2.append(s[0])

# Bring in Frames's conversations...
with open("./pkl_files/frames_list.pkl", "rb") as f:
    frames_list = pickle.load(f)

# Train the bot
trainer = ListTrainer(bot)
trainer.train(custom_list_2)
# trainer.train(frames_list)

# Function to create bot response
def bot_response(p1):

    # Intro response
    if p1.cnt == 0:
        p1.response = "Hello, how can I help you?"
        p1.cnt = p1.cnt + 1
        return p1

    else:
        try:
            # Parse the customer input using NER
            travel_chat_preproc = ner.word_preproc([[p1.text]])
            travel_ner_out = ner.word_ner_all(travel_chat_preproc)

            # See if we found any information
            len_A = len(travel_ner_out["Locations_A"]) > 0
            len_B = len(travel_ner_out["Locations_B"]) > 0
            len_R = len(travel_ner_out["Locations_R"]) > 0

            # Append found info to p1 class
            if len_A:
                # Departure Locations
                for a in travel_ner_out["Locations_A"]:
                    p1.Locations_list.append(a)
                    p1.Locations_type.append("A")

            if len_B:
                # Arrival Locations
                for b in travel_ner_out["Locations_B"]:
                    p1.Locations_list.append(b)
                    p1.Locations_type.append("B")

            if len_R:
                # Other Locations
                for r in travel_ner_out["Locations_R"]:
                    p1.Locations_list.append(r)

                    if "B" in p1.Locations_type:
                        p1.Locations_type.append("A")

                    else:
                        p1.Locations_type.append("B")

            # Dates
            if len(travel_ner_out["Dates"]) > 0:
                for b in travel_ner_out["Dates"]:
                    p1.Dates_list.append(b)

            # Money
            if len(travel_ner_out["Money"]) > 0:
                for c in travel_ner_out["Money"]:
                    p1.Money_list.append(c)

            # print(len(p1.Locations_list),len(p1.Dates_list),len(p1.Money_list))

            # Bot response
            if p1.cnt < 2:
                bot_input = bot.get_response(p1.text)
                p1.response = bot_input

            else:
                # If there is missing information ask for it
                if len(p1.Locations_list) < 2:  # Locations
                    if len(p1.Locations_list) == 0:
                        p1.response = "Where do you want to go to?"

                    else:
                        p1.response = "Where do you want to travel from?"

                elif len(p1.Dates_list) < 2 and p1.one_way == False:  # Dates
                    if len(p1.Dates_list) == 0:
                        p1.response = "When do you want to leave?"

                    else:
                        if p1.cnt_return == 0:
                            p1.response = "When do you want to return?"

                        else:
                            p1.one_way = True

                        p1.cnt_return = p1.cnt_return + 1

                elif len(p1.Money_list) < 2 and p1.no_bud == False:  # Money
                    if p1.cnt_money == 0:
                        p1.response = "How much do you want to spend?"

                    else:
                        p1.no_bud = True

                    p1.cnt_money = p1.cnt_money + 1

                else:
                    # Use the data to look for flights
                    output = rp.flight_options(
                        p1.Locations_list,
                        p1.Locations_type,
                        p1.Dates_list,
                        p1.Money_list,
                    )

                    # Update the class
                    p1.response = "Great, here are some options: \n" + output

            p1.cnt = p1.cnt + 1

            return p1

        except (KeyboardInterrupt, EOFError, SystemExit):
            return p1
