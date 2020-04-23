#!/usr/bin/env python
# coding: utf-8

#%pip install chatterbot-corpus -qq
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import ner_algorithm as ner
import pickle
import pandas as pd
import api_request_parse as rp

bot = ChatBot(
    'TravelJohnny',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3'
)

with open('./pkl_files/custom_list.pkl', 'rb') as f:
    custom_list = pickle.load(f)
custom_list_2 = []    

for s in custom_list:
    custom_list_2.append(s[0])
    
#Bring in Frames's conversations...
with open('./pkl_files/frames_list.pkl', 'rb') as f:
    frames_list = pickle.load(f)    
    
    
trainer = ListTrainer(bot)
trainer.train(custom_list_2)
#trainer.train(frames_list)

def bot_response(p1):

    if p1.cnt == 0:
        p1.response = 'Hello, how can I help you?'
        p1.cnt = p1.cnt + 1
        return p1
    else:
        try:

            #Parse the customer input
            #cust_input = input()   
            
            travel_chat_preproc = ner.word_preproc([[p1.text]])
            travel_ner_out = ner.word_ner_all(travel_chat_preproc)   

            #See if we found any information
            len_A = len(travel_ner_out['Locations_A'])>0 
            len_B = len(travel_ner_out['Locations_B'])>0
            len_R = len(travel_ner_out['Locations_R'])>0
            
            if len_A:
                for a in travel_ner_out['Locations_A']:
                        p1.Locations_list.append(a) 
                        p1.Locations_type.append('A')
            
            if len_B:
                for b in travel_ner_out['Locations_B']:
                        p1.Locations_list.append(b) 
                        p1.Locations_type.append('B')        
                    
            if len_R:        
                for r in travel_ner_out['Locations_R']:
                        p1.Locations_list.append(r) 

                        if 'B' in p1.Locations_type:
                            p1.Locations_type.append('A')
                        else:
                            p1.Locations_type.append('B')
                    
            if len(travel_ner_out['Dates'])>0:
                for b in travel_ner_out['Dates']:
                    p1.Dates_list.append(b) 

            if len(travel_ner_out['Money'])>0:
                for c in travel_ner_out['Money']:
                    p1.Money_list.append(c) 

            #print(len(p1.Locations_list),len(p1.Dates_list),len(p1.Money_list))


            if p1.cnt<2:
                bot_input = bot.get_response(p1.text)
                p1.response = bot_input
                #return p1

            else:

                if len(p1.Locations_list)<2:
                    
                    if len(p1.Locations_list)==0:
                        p1.response = 'Where do you want to go to?'
                        
                    else:
                        p1.response = 'Where do you want to travel from?'
                    #return p1

                elif len(p1.Dates_list)<2 and p1.one_way == False:
                    
                    if len(p1.Dates_list) == 0:
                        
                        p1.response = 'When do you want to leave?'
                        
                    else:

                        if p1.cnt_return == 0:
                            p1.response = 'When do you want to return?'
                            #return p1
                        else:
                            p1.one_way = True
                        #continue

                        p1.cnt_return = p1.cnt_return + 1
                    #return p1

                elif len(p1.Money_list)<2 and p1.no_bud == False:


                    if p1.cnt_money == 0:
                        p1.response = 'How much do you want to spend?'
                        #return p1
                    else:
                        p1.no_bud = True
                        #continue

                    p1.cnt_money = p1.cnt_money + 1
                    #return p1


                else:
                    #print('Great, here are some options:')

                    output = rp.flight_options(p1.Locations_list, p1.Locations_type, p1.Dates_list, p1.Money_list)

                    #print(output)
                    
                    p1.response = 'Great, here are some options: \n' + output

            p1.cnt = p1.cnt + 1
            return p1

        except(KeyboardInterrupt, EOFError, SystemExit):
            return p1


# In[8]:


# If no second loaction, ask for start location

# If no second date, assume one way

# If no money, assume cheapest

# If no dates, ask for dates, if not look at today/oneway

# If more than 3 locations -> Multicity

# Chatterbot
# https://chatterbot.readthedocs.io/en/stable/training.html

#Sky Scanner
#https://rapidapi.com/skyscanner/api/skyscanner-flight-search/endpoints


# Integration with Slack


# In[9]:


#bot.export_for_training('my_export.json')

