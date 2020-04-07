#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import pprint
import json
from pandas.io.json import json_normalize
#import flat_table


# In[3]:


data = pd.read_json('./frames/frames.json')
df = pd.DataFrame(data)
df.head() 


# In[14]:


df.shape


# In[5]:


one_convo = df['turns'][0]


# In[17]:


import pickle

convo_list = []


for conv in np.arange(0,1369):
    
    one_convo = df['turns'][conv]

    for t in np.arange(0,len(one_convo)):

        convo_list.append(one_convo[t]['text'])
    
    
#print(convo_list)

with open('frames_list.pkl', 'wb') as f:
    pickle.dump(convo_list, f)

