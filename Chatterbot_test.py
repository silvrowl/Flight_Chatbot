#!/usr/bin/env python
# coding: utf-8

# In[1]:


#%pip install chatterbot-corpus -qq
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import NER_Attempt_02 as ner
import pickle
import pandas as pd
import Response_Parsing as rp


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
#trainer.train(frames_list)
trainer.train(custom_list_2)


# In[6]:


true = True
false = False

test = {
  "Routes": [],
  "Quotes": [
    {
      "QuoteId": 1,
      "MinPrice": 80,
      "Direct": true,
      "OutboundLeg": {
        "CarrierIds": [
          1329
        ],
        "OriginId": 96474,
        "DestinationId": 60987,
        "DepartureDate": "2020-06-01T00:00:00"
      },
      "QuoteDateTime": "2020-04-08T09:32:00"
    },
    {
      "QuoteId": 2,
      "MinPrice": 78,
      "Direct": true,
      "OutboundLeg": {
        "CarrierIds": [
          838
        ],
        "OriginId": 96474,
        "DestinationId": 60987,
        "DepartureDate": "2020-06-02T00:00:00"
      },
      "QuoteDateTime": "2020-04-07T11:33:00"
    },
    {
      "QuoteId": 3,
      "MinPrice": 80,
      "Direct": true,
      "OutboundLeg": {
        "CarrierIds": [
          954
        ],
        "OriginId": 96474,
        "DestinationId": 60987,
        "DepartureDate": "2020-06-03T00:00:00"
      },
      "QuoteDateTime": "2020-04-08T09:42:00"
    },
    {
      "QuoteId": 4,
      "MinPrice": 80,
      "Direct": true,
      "OutboundLeg": {
        "CarrierIds": [
          954
        ],
        "OriginId": 96474,
        "DestinationId": 60987,
        "DepartureDate": "2020-06-04T00:00:00"
      },
      "QuoteDateTime": "2020-04-08T09:48:00"
    },
    {
      "QuoteId": 5,
      "MinPrice": 80,
      "Direct": true,
      "OutboundLeg": {
        "CarrierIds": [
          1361
        ],
        "OriginId": 96474,
        "DestinationId": 60987,
        "DepartureDate": "2020-06-05T00:00:00"
      },
      "QuoteDateTime": "2020-04-08T09:54:00"
    }
  ],
  "Places": [
    {
      "PlaceId": 60987,
      "IataCode": "JFK",
      "Name": "New York John F. Kennedy",
      "Type": "Station",
      "SkyscannerCode": "JFK",
      "CityName": "New York",
      "CityId": "NYCA",
      "CountryName": "United States"
    },
    {
      "PlaceId": 96474,
      "IataCode": "YYZ",
      "Name": "Toronto Pearson International",
      "Type": "Station",
      "SkyscannerCode": "YYZ",
      "CityName": "Toronto",
      "CityId": "YTOA",
      "CountryName": "Canada"
    }
  ],
  "Carriers": [
    {
      "CarrierId": 838,
      "Name": "Air France"
    },
    {
      "CarrierId": 954,
      "Name": "China Southern"
    },
    {
      "CarrierId": 1317,
      "Name": "Korean Air"
    },
    {
      "CarrierId": 1329,
      "Name": "Kenya Airways"
    },
    {
      "CarrierId": 1361,
      "Name": "LATAM Airlines Group"
    },
    {
      "CarrierId": 1907,
      "Name": "WestJet"
    }
  ],
  "Currencies": [
    {
      "Code": "USD",
      "Symbol": "$",
      "ThousandsSeparator": ",",
      "DecimalSeparator": ".",
      "SymbolOnLeft": true,
      "SpaceBetweenAmountAndSymbol": false,
      "RoundingCoefficient": 0,
      "DecimalDigits": 2
    }
  ]
}


# In[7]:


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
                
                output = rp.flight_options(Locations_list, Dates_list, Money_list,test)
                
                print(output)
                
                break
        
        cnt = cnt + 1
 
    except(KeyboardInterrupt, EOFError, SystemExit):
        break


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

