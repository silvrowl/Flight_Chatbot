#!/usr/bin/env python
# coding: utf-8

# # Script to do Named Entity Recognition for the purposes of a travel chat bot

#All Imports
import nltk, nltk.tag, nltk.chunk
import spacy
import numpy as np
import pandas as pd
import re
import datetime
import string
import pickle


from datetime import date
from dateutil import parser
from fuzzywuzzy import fuzz

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from nltk.tag import UnigramTagger
from nltk.corpus import brown

from nltk import conlltags2tree, tree2conlltags
from nltk.chunk import ChunkParserI 
from nltk.chunk.util import conlltags2tree 
from nltk.corpus import gazetteers 

#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt')


# # Build My own NLP
# ## Create Training Data

Sample_Text_1 = [['Hi there'],
               ['How can I help you?'],
               ['Are there any flights from Toronto to San Diego'],
               ['Yes, for which dates would you like?'],
               ['June 3rd to 10th'],
               ['How much would like to spend?'],
               ['Under 500']]


Sample_Text_2 = [['Good Morning'],
               ['How can i help you?'],
               ['I would like to see if I can travel from Seattle to Chicago tomorrow'],
               ['When would you like to come back'],
               ['In 5 weeks, but I am flexible on the day'],
               ['What is your budget'],
               ['Less than fifteen hundred dollars']]
               
Sample_Text_3 = [['Yo'],
               ['How can I help you?'],
               ['How much is it to go from San Diego to Los Angeles. I have to get there for a wedding.'],
               ['When would you like to travel'],
               ['March 1st to March 2nd'],
               ['What is your budget'],
               ['The cheapest you can find']]

Sample_Text_4 = [['Hello'],
               ['How can I help you?'],
               ['I would like to fly to San Francisco on the 5th of December'],
               ['What is your budget'],
               ['Price is no object, and I would like first class if possible']]

Sample_Text_5 = [['Hello'],
               ['How can I help you?'],
               ['I would like to fly to Portland as soon as possible'],
               ['Where are you located'],
               ['Washington'],
               ['What is your budget'],
               ['Between $400 and $500']]


Complete_Sample = Sample_Text_1 + Sample_Text_2 + Sample_Text_3 + Sample_Text_4 + Sample_Text_5

#Save custom built training data for training the bot later

#with open('custom_list.pkl', 'wb') as f:
#    pickle.dump(Complete_Sample, f)

Complete_Sample = Sample_Text_2


# ## Data Cleaning
# - Replace written numbers with values
# - Replace ASAP with today

# Functions for turning text numbers into digits

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


#Function for cleaning data using above function
def data_cleaning(sentence_list):

    sentence_list = [[text2int(sent[0])] for sent in sentence_list]   
    
    cnt = 0
    for cnt in np.arange(0,len(sentence_list)):
        sentence_list[cnt][0] = sentence_list[cnt][0].replace('as soon as possible','today')
        sentence_list[cnt][0] = sentence_list[cnt][0].replace('asap','today')
        sentence_list[cnt][0] = sentence_list[cnt][0].replace('ASAP','today')
        sentence_list[cnt][0] = sentence_list[cnt][0].replace('$',' dollars ')
    
    return sentence_list


# ## Tokenizer

#Function for tokenizing the chat

def data_token(sentence_list):
        
    token_sent = []
    
    for response in sentence_list:
        token_sent.append(sent_tokenize(response[0]))
        
    token_word = []

    for word in token_sent:
        token_word.append(word_tokenize(str(word[0])))

    return token_word

#Function for filtering stopwords and punctuation from tokenized words and lowercasing them

def filter_stopwords(token_word):
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
            
    return filtered_sent


# ## Post Tokenizaton Data Cleaning Massaging

#Function for data cleaning post tokenization, replace suffixs, and some words.

def post_token_clean(filtered_sent):

    today = date.today()
    tomorrow = date.today() + datetime.timedelta(days=1)

    filtered_sent_2 = filtered_sent.copy()
    cnt = 0 

    for word in filtered_sent:
        if word[-2:] == 'th' or word[-2:] == 'st' or word[-2:] == 'rd' or word[-2:] == 'nd':
            try:
                int(word[0])
                filtered_sent_2[cnt] = word[:-2]

            except:
                cnt2=1

        if word == 'tomorrow':        
            filtered_sent_2[cnt] =  tomorrow.strftime("%d-%m-%Y")

        if word == 'today' or word == 'now':        
            filtered_sent_2[cnt] = today.strftime("%d-%m-%Y")       

        cnt = cnt +1
        
    return filtered_sent_2


# ## Tagger

# Function for tagging words using unigram and bigram taggers, based off brown corpus

def word_tagger(words):

    brown_tagged_sents = brown.tagged_sents(categories='news')
    size = int(len(brown_tagged_sents) * 0.9)

    train_sents = brown_tagged_sents[:size]
    test_sents = brown_tagged_sents[size:]

    t0 = nltk.DefaultTagger('NN')
    t1 = nltk.UnigramTagger(train_sents, backoff=t0)
    t2 = nltk.BigramTagger(train_sents, backoff=t1)

    words_tagged = t2.tag(words)

    return words_tagged


# ## Parsers
# 
# https://www.nltk.org/api/nltk.parse.html
# 
# Run specific parsers according to each type of information we want to extract?

# ## Locations NER

# Function to fuzzy match city and state locations

def match_score(tagged_word):
    
    airports = pd.read_csv('./pkl_files/all_airports_clean.csv')
    
    user_input = tagged_word
    
    city_list = []
    city_score = []
    state_list = []
    state_score = []
    code_list = []

    ### Fuzzy Matching
    for t in np.arange(0,3487):

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

    if match_df['city_score'].max() > 80:
        return True
    
    if match_df['state_score'].max() > 80:
        return True

def match_score_list(tagged_word):
    
    airports = pd.read_csv('./pkl_files/all_airports_clean.csv')
    
    user_input = tagged_word
    
    city_list = []
    city_score = []
    state_list = []
    state_score = []
    code_list = []

    ### Fuzzy Matching
    for t in np.arange(0,3487):

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

    if match_sorted['city_score'].max() > 90:
        options_1 = match_sorted[match_sorted['city_score'] == match_sorted['city_score'].max()] 
        return options_1.head(5)
    

    elif match_sorted['city_score'].max() > 75 and match_sorted['city_score'].max() > state_sorted['state_score'].max():

        options_1 = match_sorted[match_sorted['city_score'] == match_sorted['city_score'].max()] 
        return options_1.head(5)

    else: 
        if state_sorted['state_score'].max() > 75:
            options_2 = state_sorted[state_sorted['state_score'] == match_sorted['state_score'].max()] 
            return options_2.sample(5)
        else:
            return 'no options found'


#Fucnction to compare words to gazetters word list to find locations

#If fuzzy matches > 90 on place or state, tag as location

def location_ner(words_tagged):

    #place_lower = [w.lower() for w in gazetteers.words()]

    loc_tag = words_tagged
        
    cnt=0
    for cnt in np.arange(0,len(words_tagged)):
        if match_score(words_tagged[cnt][0]):
            if words_tagged[cnt][1] == 'NN':
                #loc_tag[cnt] = (words_tagged[cnt][0],'LOCATION') 
                
                if cnt>0:
                    if words_tagged[cnt-1][0] == 'from':
                        loc_tag[cnt] = (words_tagged[cnt][0],'LOCATION_A') 
                    else:
                        loc_tag[cnt] = (words_tagged[cnt][0],'LOCATION_B') 
                        
                else:
                    loc_tag[cnt] = (words_tagged[cnt][0],'LOCATION_R') 
                

        if cnt < len(words_tagged)-1:       
            link_place = words_tagged[cnt][0] + ' ' + words_tagged[cnt+1][0]        
            if match_score(link_place):      
                if words_tagged[cnt][1] in ['JJ','NN'] and words_tagged[cnt+1][1] == 'NN':
                    
                    #loc_tag[cnt] = (link_place,'LOCATION') 
                    
                    if cnt>0:
                        if words_tagged[cnt-1][0] == 'from':
                            loc_tag[cnt] = (link_place,'LOCATION_A') 
                        else:
                            loc_tag[cnt] = (link_place,'LOCATION_B') 

                    else:
                        loc_tag[cnt] = (link_place,'LOCATION_R') 

        cnt=cnt+1
        
    return loc_tag
 

# ## Time and Dates and Money NER

#Function to find possible dates and timing and tag them as such

def dates_ner(words_tagged):

    time_tag = words_tagged.copy()

    month_lower = ['january','february','march','april','may','june',
                  'july','august','september','october','november','december',
                  'jan','feb','mar','apr','may','jun',
                  'jul','aug','sep','oct','nov','dec',
                   'day','days','week','weeks','months']

    day_lower =['monday', 'tuesday','wednesday','thursday','friday','saturday','sunday']
    
    cnt=0
    for cnt in np.arange(0,len(words_tagged)):

        if '-' in words_tagged[cnt][0]:
                    time_tag[cnt] = (words_tagged[cnt][0],'DATETIME') 

        if words_tagged[cnt][0] in month_lower:
            if words_tagged[cnt][1] == 'NN' or words_tagged[cnt][1] == 'NNS' or words_tagged[cnt][1] == 'JJ':

                try:
                    date_p2 = words_tagged[cnt-1][0] 
                    int(date_p2)
                    time_tag[cnt] = (words_tagged[cnt][0] + ' ' + date_p2 ,'DATETIME')  
                except:
                    cnt2=1    
                try:
                    date_p1 = words_tagged[cnt+1][0]  
                    int(date_p1)
                    time_tag[cnt] = (words_tagged[cnt][0] + ' ' + date_p1,'DATETIME') 
                except:
                    cnt2=1
                    
                try:
                    date_p1 = words_tagged[cnt+2][0]  
                    int(date_p1)
                    time_tag[cnt+2] = (words_tagged[cnt][0] + ' ' + date_p1,'DATETIME') 
                except:
                    cnt2=1
                    
        elif words_tagged[cnt][0] in day_lower:
            if words_tagged[cnt][1] == 'NN' or words_tagged[cnt][1] == 'NNS' or words_tagged[cnt][1] == 'JJ':
                
                try:
                    date_p2 = words_tagged[cnt-1][0] 
                    if date_p2 == 'next':
                        time_tag[cnt] = (date_p2 + ' '  + words_tagged[cnt][0],'DATETIME-DAY')  
                    else:
                        time_tag[cnt] = (words_tagged[cnt][0],'DATETIME-DAY') 
                    
                except:
                    cnt2=1       
                    
        cnt=cnt+1

        
    return time_tag


# ## Money NER
# Function to find remaining numbers and say that they are numerical phrases

def money_ner(words_tagged):
    grammar = 'NumPhrase: {<CD|NNS><CD|NNS|JJ>}'
    t_parser = nltk.RegexpParser(grammar)

    final_tree = t_parser.parse(words_tagged)
    final_tags  = tree2conlltags(final_tree)
    
    return final_tags


# ## Date Formatter
#Function to parse dates found during ner

def date_formatter(Dates):
    
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

    return date_clean

def date_formatter_2(Dates):
    
    date_clean = []
    cnt=0
    for d in Dates:
        #print(d)
        if 'next' in d[0]:
            d_plus = 7
            tmp = d[0].split(' ')
            date_clean.append(parser.parse(tmp[1]) + datetime.timedelta(days=d_plus))

        else:
            date_clean.append(parser.parse(d[0]))    

    return date_clean


# ## NER Output
#Function to place the tagged words into a dictionary

def ner_output(final_tags):

    print(final_tags)
    
    Locations_A = [tag[0] for tag in final_tags if tag[1] == 'LOCATION_A'] 
    Locations_B = [tag[0] for tag in final_tags if tag[1] == 'LOCATION_B']  
    Locations_R = [tag[0] for tag in final_tags if tag[1] == 'LOCATION_R']  
    
    Dates = [[tag[0]] for tag in final_tags if tag[1] == 'DATETIME']  
    Dates_Clean = date_formatter(Dates)
    
    Dates_2 = [[tag[0]] for tag in final_tags if tag[1] == 'DATETIME-DAY']  
    Dates_Clean_2 = date_formatter_2(Dates_2)
    
    try:
        Money = [tag[0] for tag in final_tags if tag[2] == 'B-NumPhrase']  
        int(Money[0])
        
    except:
        try:
            Money = [tag[0] for tag in final_tags if tag[2] == 'I-NumPhrase']  
            int(Money[0])
        except:
            
            try:
                Money = [tag[0] for tag in final_tags if tag[2] == 'O']  
                int(Money[0])
            except:
                Money = []
                print('money not found')
    
    print(Money)
    
    ner_output = {
      "Locations_A": Locations_A,
      "Locations_B": Locations_B,
      "Locations_R": Locations_R,  
      "Dates": Dates_Clean + Dates_Clean_2,
      "Money": Money
    }
    
    return ner_output


# ## Main
# Run the above functions, seperated into preprocessing and tagging/parsing functions

def word_preproc(raw_chat):
    
    data_clean = data_cleaning(raw_chat)
    data_tok = data_token(data_clean)
    data_fil = filter_stopwords(data_tok)
    word_proc = post_token_clean(data_fil)
    
    return word_proc

def word_ner_all(words_preproc):
    
    word_tag = word_tagger(words_preproc)
    word_tag_loc = location_ner(word_tag)
    word_tag_date = dates_ner(word_tag_loc)
    word_tag_money_parsed = money_ner(word_tag_date)
    ner_out = ner_output(word_tag_money_parsed)
    
    return ner_out


travel_chat_preproc = word_preproc(Sample_Text_1)
travel_ner_out = word_ner_all(travel_chat_preproc)
travel_ner_out 


# ## Next Steps...
# 
# ###  Logic Engine to parse NE

# In[126]:


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
    

