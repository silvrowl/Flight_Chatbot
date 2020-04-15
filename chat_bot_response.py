#!/usr/bin/env python
# coding: utf-8

#%pip install chatterbot-corpus -qq
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import NER_Attempt_02 as ner
import pickle
import pandas as pd
import Response_Parsing as rp

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
#with open('frames_list.pkl', 'rb') as f:
#    frames_list = pickle.load(f)    
    
    
trainer = ListTrainer(bot)
trainer.train(custom_list_2)

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
            if len(travel_ner_out['Locations'])>0:
                for a in travel_ner_out['Locations']:
                    p1.Locations_list.append(a) 

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
                    p1.response = 'Where do you want to travel from?'
                    #return p1

                elif len(p1.Dates_list)<2 and one_way == False:

                    if cnt_return == 0:
                        p1.response = 'When do you want to return?'
                        #return p1
                    else:
                        p1.one_way = True
                        #continue

                    p1.cnt_return = p1.cnt_return + 1
                    #return p1

                elif len(p1.Money_list)<1 and p1.no_bud == False:


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

                    output = rp.flight_options(p1.Locations_list, p1.Dates_list, p1.Money_list,test)

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

