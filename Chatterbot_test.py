#!/usr/bin/env python
# coding: utf-8

# In[1]:


#%pip install chatterbot-corpus -qq
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import NER_Attempt_02 as ner
import pickle


# In[2]:


bot = ChatBot(
    'TravelJohnny',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3'
)


# In[3]:


#Bring in George's conversations...


with open('frames_list.pkl', 'rb') as f:
    frames_list = pickle.load(f)


# In[4]:


# Bring in my conversations...
with open('custom_list.pkl', 'rb') as f:
    custom_list = pickle.load(f)

#Massage for trainer
#print(custom_list)

custom_list_2 =[]

for s in custom_list:
    custom_list_2.append(s[0])
    
print(custom_list_2)


# In[5]:


trainer = ListTrainer(bot)
trainer.train(frames_list)
trainer.train(custom_list_2)


# In[6]:


print('Hello, how can I help you?')

Locations_list = []
Dates_list = []
Money_list = []

cnt = 0
cnt_return = 0
cnt_money = 0 
no_bud = False
one_way = False

while True:
    try:
        
        #Parse the customer input
        cust_input = input()        
        travel_chat_preproc = ner.word_preproc([[cust_input]])
        travel_ner_out = ner.word_ner_all(travel_chat_preproc)   
        
        #See if we found any information
        if len(travel_ner_out['Locations'])>0:
            for a in travel_ner_out['Locations']:
                Locations_list.append(a) 
        
        if len(travel_ner_out['Dates'])>0:
            for b in travel_ner_out['Dates']:
                Dates_list.append(b) 
            
        if len(travel_ner_out['Money'])>0:
            for c in travel_ner_out['Money']:
                Money_list.append(c) 
        
        print(len(Locations_list),len(Dates_list),len(Money_list))
                
        
        if cnt<2:
            bot_input = bot.get_response(cust_input)
            print(bot_input)
        
        else:
            
            if len(Locations_list)<2:
                print('Where do you want to travel from?')
                
            elif len(Dates_list)<2 and one_way == False:
                
                if cnt_return == 0:
                    print('When do you want to return?')
                else:
                    one_way = True
                    continue
                    
                cnt_return = cnt_return + 1
                
            elif len(Money_list)<1 and no_bud == False:
                
                
                if cnt_money == 0:
                    print('How much do you want to spend?')
                else:
                    no_bud = True
                    continue
                    
                cnt_money = cnt_money + 1
                
        
            else:
                print('Great, here are some options:')
                #Use information above to search sky scanner
                
                #Convert Dates, Location (airport codes) for usage in Flight lookup
                
                #Location check/narrower
        
                #Find match score for locations
                
                
                for v in Locations_list:
                    print(ner.match_score_list(v))
                
                break
        
        cnt = cnt + 1
 
    except(KeyboardInterrupt, EOFError, SystemExit):
        break


# In[7]:


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


# In[8]:


#bot.export_for_training('my_export.json')


# In[9]:


import requests

L1 = 'YYZ'
L2 = 'JFK'
D1 = '2020-06-01'
D2 = '2020-07-01'

url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/US/USD/en-US/" + L1 + "-sky/" +  L2 + "-sky/" + D1

querystring = {"inboundpartialdate":D2}

headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': "e9ea65cb6bmsh7a9294203a09dfep163c42jsn05f9e4a2cceb"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)


# In[ ]:




