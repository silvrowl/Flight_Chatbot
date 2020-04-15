#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# In[2]:


airports = pd.read_csv('all_airports_2.csv')

for col in airports:
    airports[col] = airports[col].str.strip()


# In[3]:


airports.head()
#airports.shape


# In[4]:


from fuzzywuzzy import fuzz
Str1 = "Tornto"
Str2 = "Toronto"
Ratio = fuzz.ratio(Str1.lower(),Str2.lower())
print(Ratio)


# In[5]:


#Replace all states with written states
import csv

with open('state_abbv.tsv', 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    decode = {r[1]: r[0] for r in reader}

decode

airports.replace({'State': decode},inplace=True)

airports.to_csv('all_airports_clean.csv',index=False)


# In[6]:


### Data Cleaning

user_input = 'Washington D.C.'

city_list = []
city_score = []
state_list = []
state_score = []
code_list = []

### Fuzzy Matching
for t in np.arange(0,3587):
    
    city = airports.loc[t,'City']
    state = airports.loc[t,'State']
    code = airports.loc[t,'Code']
    
    city_list.append(city)
    city_score.append(fuzz.ratio(str(city).lower(),user_input.lower()))

    state_list.append(state)
    state_score.append(fuzz.ratio(str(state).lower(),user_input.lower()))

    code_list.append(code)

data_tuples = list(zip(city_list,city_score,state_list,state_score,code_list))
match_df = pd.DataFrame(data_tuples,columns=['city','city_score','state','state_score','code'])                       
                       
                       
### Location Duplicates

match_sorted = match_df.sort_values(by='city_score', ascending=False)
state_sorted = match_df.sort_values(by='state_score', ascending=False)


if match_sorted['city_score'].max() > 75 and match_sorted['city_score'].max() > state_sorted['state_score'].max():
    
    options_1 = match_sorted[match_sorted['city_score'] == match_sorted['city_score'].max()] 
    print(options_1)
    
else: 
    if state_sorted['state_score'].max() > 75:
        options_2 = state_sorted[state_sorted['state_score'] == match_sorted['state_score'].max()] 
        print(options_2)
    else:
        print('no options found')
        
        

### Region/Continent Matching


# In[ ]:




