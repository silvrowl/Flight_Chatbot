#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
import json
import datetime
from pandas.io.json import json_normalize
import numpy as np
import NER_Attempt_02 as ner

true = True
false = False

#Example Sky Scanner Request

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

#Function to pull quotes from skyscanner json pull

def response_to_text(test):

        quotes_df = pd.DataFrame.from_dict(test['Quotes'])
        labels_df = pd.json_normalize(quotes_df['OutboundLeg'])
        quotes2_df = pd.concat([quotes_df,labels_df],axis=1).drop(columns='OutboundLeg')
        quotes2_df['CarrierIds'] = quotes2_df['CarrierIds'].astype(str).str.replace('[','').str.replace(']','')

        carrier_dict = test['Carriers']
        carrier_dict_2 = {} 

        for t in np.arange(0,len(carrier_dict)):
            a = carrier_dict[t]['CarrierId']
            b = carrier_dict[t]['Name']
            carrier_dict_2[str(a)]=b

        quotes3_df = quotes2_df.replace({'CarrierIds': carrier_dict_2}).sort_values(by='MinPrice')

        places_dict = test['Places']
        places_dict_2 = {} 

        for t in np.arange(0,len(places_dict)):
            a = places_dict[t]['PlaceId']
            b = places_dict[t]['Name']
            places_dict_2[a]=b

        places_dict_2

        quotes4_df = quotes3_df.replace({'OriginId': places_dict_2})
        quotes5_df = quotes4_df.replace({'DestinationId': places_dict_2})
        
        return quotes5_df
        

Locations_list = ['toronto', 'san diego']
Dates_list = [datetime.datetime(2020, 6, 10, 0, 0), datetime.datetime(2020, 6, 3, 0, 0)]
Money_list = ['81']

# Function to output the results of the flight search

def flight_options(Locations_list, Dates_list, Money_list,test):
    print(Locations_list, Dates_list, Money_list)
    
    code_from_list = ner.match_score_list(Locations_list[0])['code'].values
    code_to_list = ner.match_score_list(Locations_list[1])['code'].values
    
    date_format = [d.strftime("%Y-%m-%d") for d in Dates_list]
    
    date_format.sort()
    
    print(code_from_list)
    print(code_to_list)
    
    cnt1 = 0
    
    output = 'Here are some departing flights: \n' 
    
    for st in code_from_list:
        
        if cnt1>3:
            break
        
        for en in code_to_list:
            
            if cnt1>3:
                break

            L1 = st
            L2 = en
            D1 = date_format[0]
            D2 = date_format[1]

            url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/US/USD/en-US/" + L1 + "-sky/" +  L2 + "-sky/" + D1
            #querystring = {"inboundpartialdate":D2}

            headers = { 'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                'x-rapidapi-key': "e9ea65cb6bmsh7a9294203a09dfep163c42jsn05f9e4a2cceb"}

            #response_out = requests.request("GET", url, headers=headers)
            response_in = test

            #results = response_to_text(response_in.json())
            results_1 = response_to_text(response_in)
            r1_budget = results_1[results_1['MinPrice']<int(Money_list[0])]

            for flight in np.arange(0,len(r1_budget)):

                price = r1_budget['MinPrice'][flight] 
                carr = r1_budget['CarrierIds'][flight] 
                depart = r1_budget['OriginId'][flight]
                arrive = r1_budget['DestinationId'][flight] 
                time = r1_budget['DepartureDate'][flight] 

                output_in = depart + ' to ' + arrive + ' for ' + str(price) + '$ on ' +  carr  + ' at ' + time + '\n'
                output = output + output_in

                cnt1 = cnt1 + 1
                
                if cnt1>3:
                    break
                
            

    output = output + ' and here are some returning flights: \n'            
    
    cnt2 = 0
    
    for st in code_from_list:
        
        if cnt2>3:
            break
        
        for en in code_to_list:
            
            if cnt2>3:
                break

            L1 = st
            L2 = en
            D1 = date_format[0]
            D2 = date_format[1]

            url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/US/USD/en-US/" + L2 + "-sky/" +  L1 + "-sky/" + D2
            #querystring = {"inboundpartialdate":D2}

            headers = { 'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                'x-rapidapi-key': "e9ea65cb6bmsh7a9294203a09dfep163c42jsn05f9e4a2cceb"}

            #response_in = requests.request("GET", url, headers=headers)
            response_out = test

            #results = response_to_text(response_in.json())
            results_2 = response_to_text(response_out)
            r2_budget = results_2[results_2['MinPrice']<int(Money_list[0])]

            for flight in np.arange(0,len(r2_budget)):

                price = r2_budget['MinPrice'][flight] 
                carr = r2_budget['CarrierIds'][flight] 
                depart = r2_budget['OriginId'][flight]
                arrive = r2_budget['DestinationId'][flight] 
                time = r2_budget['DepartureDate'][flight] 

                output_in = depart + ' to ' + arrive + ' for ' + str(price) + '$ on ' +  carr  + ' at ' + time + '\n'
                output = output + output_in

                cnt2 = cnt2 + 1

                if cnt2>3:
                    break

    return output
        
        
#test_response = flight_options(Locations_list, Dates_list, Money_list,test)

#print(test_response)

#Other possible repsonse from API

#url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/Canada/CAD/en/Toronto/New%2520York/2020-08-01/2020-09-01"

#headers = {
#    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
#    'x-rapidapi-key': "e9ea65cb6bmsh7a9294203a09dfep163c42jsn05f9e4a2cceb"
#    }

#response = requests.request("GET", url, headers=headers)

#print(response.text)

#test = response.json()

#test

