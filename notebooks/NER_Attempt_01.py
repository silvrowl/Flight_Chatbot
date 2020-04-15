#!/usr/bin/env python
# coding: utf-8

# In[80]:


#%pip install spacy -qq

#POC model that is able to extract locations (to and from), dates and prices ranges from conversational text.

#Imports

import nltk, nltk.tag, nltk.chunk
import spacy
import numpy as np
import pprint as pprint
from gensim.summarization import summarize
from collections import Counter

#import en_core_web_sm
#nlp = en_core_web_sm.load()
#from bs4 import BeautifulSoup
#import requests
import re
from spacy import displacy


# In[81]:


#If I want to use a prepackaged NLP

#ny_bb = 'Tlg bawa kami graduan dan family pulang.. They came for our convo but then cancelled unfortunately our flight has been cancelled too because egypt had suspended all international flight in and out. Most of airlines may not be operating till june'
#article = nlp(ny_bb)
#labels = [x.label_ for x in article.ents]
#Counter(labels)
#sentences = [x for x in article.sents]
#displacy.render(nlp(str(sentences[:])), jupyter=True, style='ent')
#print(sentences[40])


# # Build My own NLP

# ## Create Training Data

# In[82]:


#Example Chats....
nltk.download('nps_chat')
from nltk.corpus import nps_chat
chatroom = nps_chat.posts('10-19-20s_706posts.xml')
#for t in chatroom:
#    print(t)


# In[83]:


Sample_Text_1 = [['Hi there'],
               ['How can I help you?'],
               ['Are there any flights from Houston to Boston'],
               ['Yes, for which dates would you like?'],
               ['June 3rd to June 18th'],
               ['How much would like to spend?'],
               ['Under 500'],
               ['Great, Here are some options:']]


Sample_Text_2 = [['Good Morning'],
               ['How can i help you?'],
               ['I would like to see if I can travel from Seattle to Chicago tomorrow'],
               ['When would you like to come back'],
               ['In 5 days, but I am flexible on the day'],
               ['What is your budget'],
               ['Less than fifteen hundred dollars'],
               ['Great, Here are some options:']]
               
Sample_Text_3 = [['Yo'],
               ['How can I help you?'],
               ['How much is it to go from San Diego to Los Angeles. I have to get there for a wedding.'],
               ['When would you like to travel'],
               ['March 1st to March 2nd'],
               ['What is your budget'],
               ['The cheapest you can find'],
               ['Great, Here are some options:']]

Sample_Text_4 = [['Guten Tag'],
               ['How can I help you?'],
               ['I would like to fly to San Francisco on the 5th of December'],
               ['What is your budget'],
               ['Price is no object, and I would like first class if possible'],
               ['Great, Here are some options:']]

Sample_Text_5 = [['Hello'],
               ['How can I help you?'],
               ['I would like to fly to Portland as soon as possible'],
               ['Where are you located'],
               ['Washington'],
               ['What is your budget'],
               ['Between $400 and $500'],
               ['Great, Here are some options:']]


Complete_Sample = Sample_Text_1 + Sample_Text_2 + Sample_Text_3 + Sample_Text_4 + Sample_Text_5

Complete_Sample = Sample_Text_2


# ## Data Cleaning
# - Replace written numbers with values
# - Replace ASAP with today

# In[84]:


def is_number(x):
    if type(x) == str:
        x = x.replace(',', '')
    try:
        float(x)
    except:
        return False
    return True

def text2int (textnum, numwords={}):
    units = [
        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
        'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',
        'sixteen', 'seventeen', 'eighteen', 'nineteen',
    ]
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    scales = ['hundred', 'thousand', 'million', 'billion', 'trillion']
    ordinal_words = {'first':1, 'second':2, 'third':3, 'fifth':5, 'eighth':8, 'ninth':9, 'twelfth':12}
    ordinal_endings = [('ieth', 'y'), ('th', '')]

    if not numwords:
        numwords['and'] = (1, 0)
        for idx, word in enumerate(units): numwords[word] = (1, idx)
        for idx, word in enumerate(tens): numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales): numwords[word] = (10 ** (idx * 3 or 2), 0)

    textnum = textnum.replace('-', ' ')

    current = result = 0
    curstring = ''
    onnumber = False
    lastunit = False
    lastscale = False

    def is_numword(x):
        if is_number(x):
            return True
        if word in numwords:
            return True
        return False

    def from_numword(x):
        if is_number(x):
            scale = 0
            increment = int(x.replace(',', ''))
            return scale, increment
        return numwords[x]

    for word in textnum.split():
        if word in ordinal_words:
            scale, increment = (1, ordinal_words[word])
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
            onnumber = True
            lastunit = False
            lastscale = False
        else:
            for ending, replacement in ordinal_endings:
                if word.endswith(ending):
                    word = "%s%s" % (word[:-len(ending)], replacement)

            if (not is_numword(word)) or (word == 'and' and not lastscale):
                if onnumber:
                    # Flush the current number we are building
                    curstring += repr(result + current) + " "
                curstring += word + " "
                result = current = 0
                onnumber = False
                lastunit = False
                lastscale = False
            else:
                scale, increment = from_numword(word)
                onnumber = True

                if lastunit and (word not in scales):                                                                                                                                                                                                                                         
                    # Assume this is part of a string of individual numbers to                                                                                                                                                                                                                
                    # be flushed, such as a zipcode "one two three four five"                                                                                                                                                                                                                 
                    curstring += repr(result + current)                                                                                                                                                                                                                                       
                    result = current = 0                                                                                                                                                                                                                                                      

                if scale > 1:                                                                                                                                                                                                                                                                 
                    current = max(1, current)                                                                                                                                                                                                                                                 

                current = current * scale + increment                                                                                                                                                                                                                                         
                if scale > 100:                                                                                                                                                                                                                                                               
                    result += current                                                                                                                                                                                                                                                         
                    current = 0                                                                                                                                                                                                                                                               

                lastscale = False                                                                                                                                                                                                              
                lastunit = False                                                                                                                                                
                if word in scales:                                                                                                                                                                                                             
                    lastscale = True                                                                                                                                                                                                         
                elif word in units:                                                                                                                                                                                                             
                    lastunit = True

    if onnumber:
        curstring += repr(result + current)

    return curstring
 
Complete_Sample_2 = [[text2int(sent[0])] for sent in Complete_Sample]   

#Complete_Sample_2


# In[85]:


cnt = 0
for cnt in np.arange(0,len(Complete_Sample_2)):
    Complete_Sample_2[cnt][0] = Complete_Sample_2[cnt][0].replace('as soon as possible','today')
    Complete_Sample_2[cnt][0] = Complete_Sample_2[cnt][0].replace('asap','today')
    Complete_Sample_2[cnt][0] = Complete_Sample_2[cnt][0].replace('ASAP','today')
    
#Complete_Sample_2


# In[86]:


cnt = 0
for cnt in np.arange(0,len(Complete_Sample_2)):
    Complete_Sample_2[cnt][0] = Complete_Sample_2[cnt][0].replace('$','dollars ')

Complete_Sample_2


# ## Tokenizer

# In[87]:


#nltk.download('punkt')
from nltk.tokenize import sent_tokenize

token_sent = []

for response in Complete_Sample_2:
    token_sent.append(sent_tokenize(response[0]))

print(token_sent[0])


# In[88]:


token_word = []
from nltk.tokenize import word_tokenize
for word in token_sent:
    token_word.append(word_tokenize(str(word[0])))

print(token_word)


# In[89]:


#nltk.download('stopwords')
from nltk.corpus import stopwords
import string

stop_words = stopwords.words('english')
no_punct = [] 
            
for t in token_word:
    for ts in t:
        if ts not in string.punctuation:
            no_punct.append(ts)

data_lower = [w.lower() for w in no_punct]

filtered_sent=[]

for w in data_lower:
    if w not in stop_words:
        filtered_sent.append(w)

print(filtered_sent)


# In[90]:


#Stemmer and Lemmatizer

#from nltk.stem import PorterStemmer
#from nltk.stem import LancasterStemmer

#ps= PorterStemmer()
#ls = LancasterStemmer()

#psstemmed_words=[]
#lsstemmed_words = []

#for w in filtered_sent:    
    #psstemmed_words.append(ps.stem(w))
    #lsstemmed_words.append(ls.stem(w))
    #print("Words "+w+ "    PS :"+ps.stem(w) + "     LS : "+ls.stem(w))

    
#from nltk.stem.wordnet import WordNetLemmatizer
#nltk.download('wordnet')

#lem = WordNetLemmatizer()
#for word in filtered_sent:
#    print ("{0:20}{1:20}".format(word,lem.lemmatize(word, pos ="v")))

#today = date.today()
#d1 = today.strftime("%B %d")

#print(str(d1))


# ## Data Cleaning Massaging

# In[91]:


#Data Cleaning / Massaging

# Places -> Fine

# Time and Dates
import datetime
from datetime import date

today = date.today()
tomorrow = date.today() + datetime.timedelta(days=1)

filtered_sent_2 = filtered_sent.copy()
cnt = 0 

for word in filtered_sent:
    if word[-2:] == 'th' or word[-2:] == 'st' or word[-2:] == 'rd' or word[-2:] == 'nd':
        try:
            int(word[0])
            print(word[:-2])
            filtered_sent_2[cnt] = word[:-2]

        except:
            cnt2=1
            
    if word == 'tomorrow':        
        filtered_sent_2[cnt] =  tomorrow.strftime("%d-%m-%Y")
        #print(d2)
        
    if word == 'today' or word == 'now':        
        filtered_sent_2[cnt] = today.strftime("%d-%m-%Y")       
        #print(d1)    
        
    cnt = cnt +1

#filtered_sent_2


# ## Tagger

# In[92]:


#dl_pos =  nltk.pos_tag(data_lower)
#dl_pos = default_tagger.tag(data_lower)


# In[93]:


#nltk.download('averaged_perceptron_tagger')
#nltk.pos_tag(data_lower)
from nltk.tag import UnigramTagger
from nltk.corpus import brown

brown_tagged_sents = brown.tagged_sents(categories='news')

size = int(len(brown_tagged_sents) * 0.9)

train_sents = brown_tagged_sents[:size]
test_sents = brown_tagged_sents[size:]

t0 = nltk.DefaultTagger('NN')
t1 = nltk.UnigramTagger(train_sents, backoff=t0)
t2 = nltk.BigramTagger(train_sents, backoff=t1)
#t2.tag(filtered_sent_2)


# ## Parsers
# 
# https://www.nltk.org/api/nltk.parse.html
# 
# Run specific parsers according to each type of information we want to extract?

# ## Locations

# In[94]:


### Locations
#https://www.geeksforgeeks.org/nlp-location-tags-extraction/
import numpy as np
from nltk.chunk import ChunkParserI 
from nltk.chunk.util import conlltags2tree 
from nltk.corpus import gazetteers 
  
#sent_pos = nltk.pos_tag(data_lower)    
words_tagged = t2.tag(filtered_sent_2)
place_lower = [w.lower() for w in gazetteers.words()]

loc_tag = words_tagged

cnt=0
for cnt in np.arange(1,len(words_tagged)-1):
    if words_tagged[cnt][0] in place_lower:
        if words_tagged[cnt][1] == 'NN':
            print(words_tagged[cnt][0])
            loc_tag[cnt] = (words_tagged[cnt][0],'LOCATION') 
            
    link_place = words_tagged[cnt][0] + ' ' + words_tagged[cnt+1][0]        
    if link_place in place_lower:      
        if words_tagged[cnt][1] in ['JJ','NN'] and words_tagged[cnt+1][1] == 'NN':
            print(link_place)
            loc_tag[cnt] = (link_place,'LOCATION') 
            
    cnt=cnt+1

#print(loc_tag)
#'/' in '25/03/2020'


# ## Time and Dates and Money
# 

# In[95]:


time_tag = loc_tag.copy()

month_lower = ['january','february','march','april','may','june',
              'july','august','september','october','november','december',
              'jan','feb','mar','apr','may','jun',
              'jul','aug','sep','oct','nov','dec',
               'day','days','week','weeks','months']

cnt=0
for cnt in np.arange(1,len(loc_tag)-1):
    
    if '-' in loc_tag[cnt][0]:
                time_tag[cnt] = (loc_tag[cnt][0],'DATETIME') 
    
    if loc_tag[cnt][0] in month_lower:
        if loc_tag[cnt][1] == 'NN' or loc_tag[cnt][1] == 'NNS':
                   
            date_p2 = loc_tag[cnt-1][0]        
            try:
                int(date_p2)
                time_tag[cnt] = (loc_tag[cnt][0] + ' ' + date_p2 ,'DATETIME') 
                #time_tag[cnt-1] = ('','NN') 
            except:
                cnt2=1    
                
            date_p1 = loc_tag[cnt+1][0]        
            try:
                int(date_p1)
                time_tag[cnt] = (loc_tag[cnt][0] + ' ' + date_p1,'DATETIME') 
                #time_tag[cnt+1] = ('','NN') 
            except:
                cnt2=1
    cnt=cnt+1

#print(loc_tag)

grammar = 'NumPhrase: {<CD><CD|NNS|JJ>}'
t_parser = nltk.RegexpParser(grammar)

final_tree = t_parser.parse(time_tag)


# In[96]:


from nltk import conlltags2tree, tree2conlltags

print(final_tree)

final_tags  = tree2conlltags(final_tree)
print(final_tags)


# In[97]:


#Find all important tags
Locations = [[tag[0]] for tag in final_tags if tag[1] == 'LOCATION']  
Locations

Dates = [[tag[0]] for tag in final_tags if tag[1] == 'DATETIME']  
Dates

Money = [[tag[0]] for tag in final_tags if tag[2] == 'B-NumPhrase']  
Money

print(Locations,Dates,Money)


# ### Convert all dates into standard format

# In[98]:


from dateutil import parser

date_clean = []

cnt=0
for d in Dates:
    
    if 'day' in d[0]:
        tmp = d[0].split(' ')
        d_plus = int(tmp[1])
        date_clean.append(date.today() + datetime.timedelta(days=d_plus))
    
    elif 'week' in d[0]:
        tmp = d[0].split(' ')
        d_plus = int(tmp[1])
        date_clean.append(date.today() + datetime.timedelta(days=d_plus*7))
        
    elif 'month' in d[0]:
        tmp = d[0].split(' ')
        d_plus = int(tmp[1])
        date_clean.append(date.today() + datetime.timedelta(days=d_plus*30))
        
    else:
        date_clean.append(parser.parse(d[0]))    
    
print(date_clean)


# ## NLTK NER
# Chunking?

# In[99]:


#nltk.download('maxent_ne_chunker')
#nltk.download('words')
from nltk import ne_chunk, pos_tag
chunked = ne_chunk(loc_tag)

print(chunked)


# ## Text Categorizer

# ## Custom Components

# ## Logic Engine to parse NE

# In[100]:


# If no second loaction, ask for start location

# If no second date, assume one way

# If no money, assume cheapest

# If no dates, ask for dates, if not look at today/oneway

# If more than 3 locations -> Multicity

# Chatterbot
# https://chatterbot.readthedocs.io/en/stable/training.html

# Start Presentation Tomorrow
    # Intro
    # Methodology / Challenges
    # Tech Stack / Processs
    # Demo of Tagging
    # Results/Next Steps
    

