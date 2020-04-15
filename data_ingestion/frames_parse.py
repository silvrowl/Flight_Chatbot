#!/usr/bin/env python
# coding: utf-8
# Script for decoding and pickling frames conversation data

import pandas as pd
import numpy as np
import pprint
import json
import pickle
from pandas.io.json import json_normalize

data = pd.read_json('./frames/frames.json')
df = pd.DataFrame(data)
df.head() 

convo_list = []

for conv in np.arange(0,1369):    
    one_convo = df['turns'][conv]
    for t in np.arange(0,len(one_convo)):
        convo_list.append(one_convo[t]['text'])
    
with open('frames_list.pkl', 'wb') as f:
    pickle.dump(convo_list, f)