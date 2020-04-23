#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
import json
import datetime
from datetime import datetime
from pandas.io.json import json_normalize
import numpy as np
import ner_algorithm as ner

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
        
# Function to output the results of the flight search

def flight_options(Locations_list, Locations_type, Dates_list, Money_list):
    
    
    print(Locations_list, Locations_type, Dates_list, Money_list)
    
    code_from_list = ner.match_score_list(Locations_list[Locations_type.index('A')])['code'].values
    code_to_list = ner.match_score_list(Locations_list[Locations_type.index('B')])['code'].values
        
    
    date_format = [d.strftime("%Y-%m-%d") for d in Dates_list]
    
    date_format.sort()
    
    print(code_from_list)
    print(code_to_list)
    
    cnt1 = 0
    
    output = 'Here are some departing flights: \n' 
    
    r1_budget = pd.DataFrame(columns=['QuoteId','MinPrice','Direct','QuoteDateTime', 'CarrierIds', 'OriginId','DestinationId','DepartureDate'])
    
    for st in code_from_list:        
        for en in code_to_list:
            
            try:
                L1 = st
                L2 = en
                D1 = date_format[0]
                D2 = date_format[1]

                url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/US/USD/en-US/" + L1 + "-sky/" +  L2 + "-sky/" + D1
                #querystring = {"inboundpartialdate":D2}

                headers = { 'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                    'x-rapidapi-key': "e9ea65cb6bmsh7a9294203a09dfep163c42jsn05f9e4a2cceb"}

                response_in = requests.request("GET", url, headers=headers)

                #print(response_in.json())
                results_1 = response_to_text(response_in.json())
                r1_budget_new = results_1[results_1['MinPrice']<int(max(Money_list))]
                r1_budget = pd.concat([r1_budget,r1_budget_new])             
                             
                #response_in = test
                #results_1 = response_to_text(response_in)     

            except:
                print( st + ' to ' + en + ' flight not found \n' )

                             
    r1_budget['DepartureDate'] = pd.to_datetime(r1_budget['DepartureDate'])
    diff = r1_budget['DepartureDate'] - datetime.strptime(D1,'%Y-%m-%d')
    r1_budget['time_delta'] = diff.abs()
    r1_budget.sort_values(by='time_delta',ignore_index=True,inplace=True)

    #print(r1_budget)

    for flight in np.arange(0,len(r1_budget)-1):

        price = r1_budget['MinPrice'][flight] 
        carr = r1_budget['CarrierIds'][flight] 
        depart = r1_budget['OriginId'][flight]
        arrive = r1_budget['DestinationId'][flight] 
        time = r1_budget['DepartureDate'][flight]

        output_in = depart + ' to ' + arrive + ' for ' + str(price) + '$ on ' +  carr  + ' on ' + time.strftime("%Y-%m-%d") + '\n'
        output = output + output_in

        cnt1 = cnt1 + 1

        if cnt1>3:
            break     
                             
                             
    output = output + '\n And here are some returning flights: \n'            
    
    r2_budget = pd.DataFrame(columns=['QuoteId','MinPrice','Direct','QuoteDateTime', 'CarrierIds', 'OriginId','DestinationId','DepartureDate'])
    
    cnt2 = 0
    
    for st in code_from_list:        
        for en in code_to_list:
            
            try:

                L1 = st
                L2 = en
                D1 = date_format[0]
                D2 = date_format[1]

                url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/US/USD/en-US/" + L2 + "-sky/" +  L1 + "-sky/" + D2
                #querystring = {"inboundpartialdate":D2}

                headers = { 'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                    'x-rapidapi-key': "e9ea65cb6bmsh7a9294203a09dfep163c42jsn05f9e4a2cceb"}

                response_out = requests.request("GET", url, headers=headers)
                
                #print(response_out.json())
                
                results_2 = response_to_text(response_out.json())
                r2_budget_new = results_2[results_2['MinPrice']<int(max(Money_list))]
                r2_budget = pd.concat([r2_budget,r2_budget_new])    

                #response_out = test
                #results_2 = response_to_text(response_out)
     
            except:
                print( st + ' to ' + en + ' flight not found \n' )
    
    r2_budget['DepartureDate'] = pd.to_datetime(r2_budget['DepartureDate'])
    diff = r2_budget['DepartureDate'] - datetime.strptime(D2,'%Y-%m-%d')
    r2_budget['time_delta'] = diff.abs()
    r2_budget.sort_values(by='time_delta',ignore_index=True,inplace=True)

    for flight in np.arange(0,len(r2_budget)-1):

        price = r2_budget['MinPrice'][flight] 
        carr = r2_budget['CarrierIds'][flight] 
        depart = r2_budget['OriginId'][flight]
        arrive = r2_budget['DestinationId'][flight] 
        time = r2_budget['DepartureDate'][flight] 

        output_in = depart + ' to ' + arrive + ' for ' + str(price) + '$ on ' +  carr  + ' on ' + time.strftime("%Y-%m-%d") + '\n'
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

