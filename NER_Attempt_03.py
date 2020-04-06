{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Script to do Named Entity Recognition for the purposes of a travel chat bot"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "[nltk_data] Downloading package averaged_perceptron_tagger to\n",
      "[nltk_data]     /home/dan/nltk_data...\n",
      "[nltk_data]   Package averaged_perceptron_tagger is already up-to-\n",
      "[nltk_data]       date!\n",
      "[nltk_data] Downloading package punkt to /home/dan/nltk_data...\n",
      "[nltk_data]   Package punkt is already up-to-date!\n"
     ]
    },
    {
     "data": {
      "text/plain": [
       "True"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#All Imports\n",
    "import nltk, nltk.tag, nltk.chunk\n",
    "import spacy\n",
    "import numpy as np\n",
    "import re\n",
    "import datetime\n",
    "import string\n",
    "\n",
    "from datetime import date\n",
    "from dateutil import parser\n",
    "\n",
    "from nltk.tokenize import sent_tokenize\n",
    "from nltk.tokenize import word_tokenize\n",
    "from nltk.corpus import stopwords\n",
    "\n",
    "from nltk.tag import UnigramTagger\n",
    "from nltk.corpus import brown\n",
    "\n",
    "from nltk import conlltags2tree, tree2conlltags\n",
    "from nltk.chunk import ChunkParserI \n",
    "from nltk.chunk.util import conlltags2tree \n",
    "from nltk.corpus import gazetteers \n",
    "\n",
    "nltk.download('averaged_perceptron_tagger')\n",
    "nltk.download('punkt')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Build My own NLP"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Create Training Data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "Sample_Text_1 = [['Hi there'],\n",
    "               ['How can I help you?'],\n",
    "               ['Are there any flights from Houston to San Diego'],\n",
    "               ['Yes, for which dates would you like?'],\n",
    "               ['June 3rd to June 18th'],\n",
    "               ['How much would like to spend?'],\n",
    "               ['Under 500'],\n",
    "               ['Great, Here are some options:']]\n",
    "\n",
    "\n",
    "Sample_Text_2 = [['Good Morning'],\n",
    "               ['How can i help you?'],\n",
    "               ['I would like to see if I can travel from Seattle to Chicago tomorrow'],\n",
    "               ['When would you like to come back'],\n",
    "               ['In 5 weeks, but I am flexible on the day'],\n",
    "               ['What is your budget'],\n",
    "               ['Less than fifteen hundred dollars'],\n",
    "               ['Great, Here are some options:']]\n",
    "               \n",
    "Sample_Text_3 = [['Yo'],\n",
    "               ['How can I help you?'],\n",
    "               ['How much is it to go from San Diego to Los Angeles. I have to get there for a wedding.'],\n",
    "               ['When would you like to travel'],\n",
    "               ['March 1st to March 2nd'],\n",
    "               ['What is your budget'],\n",
    "               ['The cheapest you can find'],\n",
    "               ['Great, Here are some options:']]\n",
    "\n",
    "Sample_Text_4 = [['Guten Tag'],\n",
    "               ['How can I help you?'],\n",
    "               ['I would like to fly to San Francisco on the 5th of December'],\n",
    "               ['What is your budget'],\n",
    "               ['Price is no object, and I would like first class if possible'],\n",
    "               ['Great, Here are some options:']]\n",
    "\n",
    "Sample_Text_5 = [['Hello'],\n",
    "               ['How can I help you?'],\n",
    "               ['I would like to fly to Portland as soon as possible'],\n",
    "               ['Where are you located'],\n",
    "               ['Washington'],\n",
    "               ['What is your budget'],\n",
    "               ['Between $400 and $500'],\n",
    "               ['Great, Here are some options:']]\n",
    "\n",
    "\n",
    "Complete_Sample = Sample_Text_1 + Sample_Text_2 + Sample_Text_3 + Sample_Text_4 + Sample_Text_5\n",
    "\n",
    "Complete_Sample = Sample_Text_2"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Data Cleaning\n",
    "- Replace written numbers with values\n",
    "- Replace ASAP with today"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Functions for turning text numbers into digits\n",
    "\n",
    "def is_number(x):\n",
    "    if type(x) == str:\n",
    "        x = x.replace(',', '')\n",
    "    try:\n",
    "        float(x)\n",
    "    except:\n",
    "        return False\n",
    "    return True\n",
    "\n",
    "def text2int (textnum, numwords={}):\n",
    "    units = [\n",
    "        'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',\n",
    "        'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen',\n",
    "        'sixteen', 'seventeen', 'eighteen', 'nineteen',\n",
    "    ]\n",
    "    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']\n",
    "    scales = ['hundred', 'thousand', 'million', 'billion', 'trillion']\n",
    "    ordinal_words = {'first':1, 'second':2, 'third':3, 'fifth':5, 'eighth':8, 'ninth':9, 'twelfth':12}\n",
    "    ordinal_endings = [('ieth', 'y'), ('th', '')]\n",
    "\n",
    "    if not numwords:\n",
    "        numwords['and'] = (1, 0)\n",
    "        for idx, word in enumerate(units): numwords[word] = (1, idx)\n",
    "        for idx, word in enumerate(tens): numwords[word] = (1, idx * 10)\n",
    "        for idx, word in enumerate(scales): numwords[word] = (10 ** (idx * 3 or 2), 0)\n",
    "\n",
    "    textnum = textnum.replace('-', ' ')\n",
    "\n",
    "    current = result = 0\n",
    "    curstring = ''\n",
    "    onnumber = False\n",
    "    lastunit = False\n",
    "    lastscale = False\n",
    "\n",
    "    def is_numword(x):\n",
    "        if is_number(x):\n",
    "            return True\n",
    "        if word in numwords:\n",
    "            return True\n",
    "        return False\n",
    "\n",
    "    def from_numword(x):\n",
    "        if is_number(x):\n",
    "            scale = 0\n",
    "            increment = int(x.replace(',', ''))\n",
    "            return scale, increment\n",
    "        return numwords[x]\n",
    "\n",
    "    for word in textnum.split():\n",
    "        if word in ordinal_words:\n",
    "            scale, increment = (1, ordinal_words[word])\n",
    "            current = current * scale + increment\n",
    "            if scale > 100:\n",
    "                result += current\n",
    "                current = 0\n",
    "            onnumber = True\n",
    "            lastunit = False\n",
    "            lastscale = False\n",
    "        else:\n",
    "            for ending, replacement in ordinal_endings:\n",
    "                if word.endswith(ending):\n",
    "                    word = \"%s%s\" % (word[:-len(ending)], replacement)\n",
    "\n",
    "            if (not is_numword(word)) or (word == 'and' and not lastscale):\n",
    "                if onnumber:\n",
    "                    # Flush the current number we are building\n",
    "                    curstring += repr(result + current) + \" \"\n",
    "                curstring += word + \" \"\n",
    "                result = current = 0\n",
    "                onnumber = False\n",
    "                lastunit = False\n",
    "                lastscale = False\n",
    "            else:\n",
    "                scale, increment = from_numword(word)\n",
    "                onnumber = True\n",
    "\n",
    "                if lastunit and (word not in scales):                                                                                                                                                                                                                                         \n",
    "                    # Assume this is part of a string of individual numbers to                                                                                                                                                                                                                \n",
    "                    # be flushed, such as a zipcode \"one two three four five\"                                                                                                                                                                                                                 \n",
    "                    curstring += repr(result + current)                                                                                                                                                                                                                                       \n",
    "                    result = current = 0                                                                                                                                                                                                                                                      \n",
    "\n",
    "                if scale > 1:                                                                                                                                                                                                                                                                 \n",
    "                    current = max(1, current)                                                                                                                                                                                                                                                 \n",
    "\n",
    "                current = current * scale + increment                                                                                                                                                                                                                                         \n",
    "                if scale > 100:                                                                                                                                                                                                                                                               \n",
    "                    result += current                                                                                                                                                                                                                                                         \n",
    "                    current = 0                                                                                                                                                                                                                                                               \n",
    "\n",
    "                lastscale = False                                                                                                                                                                                                              \n",
    "                lastunit = False                                                                                                                                                \n",
    "                if word in scales:                                                                                                                                                                                                             \n",
    "                    lastscale = True                                                                                                                                                                                                         \n",
    "                elif word in units:                                                                                                                                                                                                             \n",
    "                    lastunit = True\n",
    "\n",
    "    if onnumber:\n",
    "        curstring += repr(result + current)\n",
    "\n",
    "    return curstring"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Function for cleaning data using above function\n",
    "def data_cleaning(sentence_list):\n",
    "\n",
    "    sentence_list = [[text2int(sent[0])] for sent in sentence_list]   \n",
    "    \n",
    "    cnt = 0\n",
    "    for cnt in np.arange(0,len(sentence_list)):\n",
    "        sentence_list[cnt][0] = sentence_list[cnt][0].replace('as soon as possible','today')\n",
    "        sentence_list[cnt][0] = sentence_list[cnt][0].replace('asap','today')\n",
    "        sentence_list[cnt][0] = sentence_list[cnt][0].replace('ASAP','today')\n",
    "        sentence_list[cnt][0] = sentence_list[cnt][0].replace('$','dollars ')\n",
    "    \n",
    "    return sentence_list"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Tokenizer"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Function for tokenizing the chat\n",
    "\n",
    "def data_token(sentence_list):\n",
    "        \n",
    "    token_sent = []\n",
    "    \n",
    "    for response in sentence_list:\n",
    "        token_sent.append(sent_tokenize(response[0]))\n",
    "        \n",
    "    token_word = []\n",
    "\n",
    "    for word in token_sent:\n",
    "        token_word.append(word_tokenize(str(word[0])))\n",
    "\n",
    "    return token_word"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "#Function for filtering stopwords and punctuation from tokenized words and lowercasing them\n",
    "\n",
    "def filter_stopwords(token_word):\n",
    "    stop_words = stopwords.words('english')\n",
    "    no_punct = [] \n",
    "\n",
    "    for t in token_word:\n",
    "        for ts in t:\n",
    "            if ts not in string.punctuation:\n",
    "                no_punct.append(ts)\n",
    "\n",
    "    data_lower = [w.lower() for w in no_punct]\n",
    "\n",
    "    filtered_sent=[]\n",
    "\n",
    "    for w in data_lower:\n",
    "        if w not in stop_words:\n",
    "            filtered_sent.append(w)\n",
    "            \n",
    "    return filtered_sent"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Post Tokenizaton Data Cleaning Massaging"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Function for data cleaning post tokenization, replace suffixs, and some words.\n",
    "\n",
    "def post_token_clean(filtered_sent):\n",
    "\n",
    "    today = date.today()\n",
    "    tomorrow = date.today() + datetime.timedelta(days=1)\n",
    "\n",
    "    filtered_sent_2 = filtered_sent.copy()\n",
    "    cnt = 0 \n",
    "\n",
    "    for word in filtered_sent:\n",
    "        if word[-2:] == 'th' or word[-2:] == 'st' or word[-2:] == 'rd' or word[-2:] == 'nd':\n",
    "            try:\n",
    "                int(word[0])\n",
    "                filtered_sent_2[cnt] = word[:-2]\n",
    "\n",
    "            except:\n",
    "                cnt2=1\n",
    "\n",
    "        if word == 'tomorrow':        \n",
    "            filtered_sent_2[cnt] =  tomorrow.strftime(\"%d-%m-%Y\")\n",
    "\n",
    "        if word == 'today' or word == 'now':        \n",
    "            filtered_sent_2[cnt] = today.strftime(\"%d-%m-%Y\")       \n",
    "\n",
    "        cnt = cnt +1\n",
    "        \n",
    "    return filtered_sent_2"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Tagger"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Function for tagging words using unigram and bigram taggers, based off brown corpus\n",
    "\n",
    "def word_tagger(words):\n",
    "\n",
    "    brown_tagged_sents = brown.tagged_sents(categories='news')\n",
    "    size = int(len(brown_tagged_sents) * 0.9)\n",
    "\n",
    "    train_sents = brown_tagged_sents[:size]\n",
    "    test_sents = brown_tagged_sents[size:]\n",
    "\n",
    "    t0 = nltk.DefaultTagger('NN')\n",
    "    t1 = nltk.UnigramTagger(train_sents, backoff=t0)\n",
    "    t2 = nltk.BigramTagger(train_sents, backoff=t1)\n",
    "\n",
    "    words_tagged = t2.tag(words)\n",
    "\n",
    "    return words_tagged"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Parsers\n",
    "\n",
    "https://www.nltk.org/api/nltk.parse.html\n",
    "\n",
    "Run specific parsers according to each type of information we want to extract?"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Locations NER"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Fucnction to compare words to gazetters word list to find locations\n",
    "\n",
    "def location_ner(words_tagged):\n",
    "\n",
    "    place_lower = [w.lower() for w in gazetteers.words()]\n",
    "\n",
    "    loc_tag = words_tagged\n",
    "\n",
    "    cnt=0\n",
    "    for cnt in np.arange(1,len(words_tagged)-1):\n",
    "        if words_tagged[cnt][0] in place_lower:\n",
    "            if words_tagged[cnt][1] == 'NN':\n",
    "                loc_tag[cnt] = (words_tagged[cnt][0],'LOCATION') \n",
    "\n",
    "        link_place = words_tagged[cnt][0] + ' ' + words_tagged[cnt+1][0]        \n",
    "        if link_place in place_lower:      \n",
    "            if words_tagged[cnt][1] in ['JJ','NN'] and words_tagged[cnt+1][1] == 'NN':\n",
    "                loc_tag[cnt] = (link_place,'LOCATION') \n",
    "\n",
    "        cnt=cnt+1\n",
    "        \n",
    "    return loc_tag"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Time and Dates and Money NER\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Function to find possible dates and timing and tag them as such\n",
    "\n",
    "def dates_ner(words_tagged):\n",
    "\n",
    "    time_tag = words_tagged.copy()\n",
    "\n",
    "    month_lower = ['january','february','march','april','may','june',\n",
    "                  'july','august','september','october','november','december',\n",
    "                  'jan','feb','mar','apr','may','jun',\n",
    "                  'jul','aug','sep','oct','nov','dec',\n",
    "                   'day','days','week','weeks','months']\n",
    "\n",
    "    cnt=0\n",
    "    for cnt in np.arange(1,len(words_tagged)-1):\n",
    "\n",
    "        if '-' in words_tagged[cnt][0]:\n",
    "                    time_tag[cnt] = (words_tagged[cnt][0],'DATETIME') \n",
    "\n",
    "        if words_tagged[cnt][0] in month_lower:\n",
    "            if words_tagged[cnt][1] == 'NN' or words_tagged[cnt][1] == 'NNS':\n",
    "\n",
    "                date_p2 = words_tagged[cnt-1][0]        \n",
    "                try:\n",
    "                    int(date_p2)\n",
    "                    time_tag[cnt] = (words_tagged[cnt][0] + ' ' + date_p2 ,'DATETIME')  \n",
    "                except:\n",
    "                    cnt2=1    \n",
    "\n",
    "                date_p1 = words_tagged[cnt+1][0]        \n",
    "                try:\n",
    "                    int(date_p1)\n",
    "                    time_tag[cnt] = (words_tagged[cnt][0] + ' ' + date_p1,'DATETIME') \n",
    "                except:\n",
    "                    cnt2=1\n",
    "        cnt=cnt+1\n",
    "        \n",
    "    return time_tag"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Money NER"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Function to find remaining numbers and say that they are numerical phrases\n",
    "\n",
    "def money_ner(words_tagged):\n",
    "    grammar = 'NumPhrase: {<CD><CD|NNS|JJ>}'\n",
    "    t_parser = nltk.RegexpParser(grammar)\n",
    "\n",
    "    final_tree = t_parser.parse(words_tagged)\n",
    "    final_tags  = tree2conlltags(final_tree)\n",
    "    \n",
    "    return final_tags"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Date Formatter"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Function to parse dates found during ner\n",
    "\n",
    "def date_formatter(Dates):\n",
    "    \n",
    "    date_clean = []\n",
    "    cnt=0\n",
    "    for d in Dates:\n",
    "\n",
    "        if 'day' in d[0]:\n",
    "            tmp = d[0].split(' ')\n",
    "            d_plus = int(tmp[1])\n",
    "            date_clean.append(date.today() + datetime.timedelta(days=d_plus))\n",
    "\n",
    "        elif 'week' in d[0]:\n",
    "            tmp = d[0].split(' ')\n",
    "            d_plus = int(tmp[1])\n",
    "            date_clean.append(date.today() + datetime.timedelta(days=d_plus*7))\n",
    "\n",
    "        elif 'month' in d[0]:\n",
    "            tmp = d[0].split(' ')\n",
    "            d_plus = int(tmp[1])\n",
    "            date_clean.append(date.today() + datetime.timedelta(days=d_plus*30))\n",
    "\n",
    "        else:\n",
    "            date_clean.append(parser.parse(d[0]))    \n",
    "\n",
    "    return date_clean"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## NER Output"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Function to place the tagged words into a dictionary\n",
    "\n",
    "def ner_output(final_tags):\n",
    "\n",
    "    Locations = [tag[0] for tag in final_tags if tag[1] == 'LOCATION']  \n",
    "    Dates = [[tag[0]] for tag in final_tags if tag[1] == 'DATETIME']  \n",
    "    Dates_Clean = date_formatter(Dates)\n",
    "    Money = [tag[0] for tag in final_tags if tag[2] == 'B-NumPhrase']  \n",
    "\n",
    "    ner_output = {\n",
    "      \"Locations\": Locations,\n",
    "      \"Dates\": Dates_Clean,\n",
    "      \"Money\": Money\n",
    "    }\n",
    "    \n",
    "    return ner_output"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Main"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{'Locations': ['houston', 'san diego'],\n",
       " 'Dates': [datetime.datetime(2020, 6, 3, 0, 0),\n",
       "  datetime.datetime(2020, 6, 18, 0, 0)],\n",
       " 'Money': ['500']}"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Run the above functions, seperated into preprocessing and tagging/parsing functions\n",
    "\n",
    "def word_preproc(raw_chat):\n",
    "    \n",
    "    data_clean = data_cleaning(raw_chat)\n",
    "    data_tok = data_token(data_clean)\n",
    "    data_fil = filter_stopwords(data_tok)\n",
    "    word_proc = post_token_clean(data_fil)\n",
    "    \n",
    "    return word_proc\n",
    "\n",
    "def word_ner_all(words_preproc):\n",
    "    \n",
    "    word_tag = word_tagger(words_preproc)\n",
    "    word_tag_loc = location_ner(word_tag)\n",
    "    word_tag_date = dates_ner(word_tag_loc)\n",
    "    word_tag_money_parsed = money_ner(word_tag_date)\n",
    "    ner_out = ner_output(word_tag_money_parsed)\n",
    "    \n",
    "    return ner_out\n",
    "\n",
    "\n",
    "travel_chat_preproc = word_preproc(Sample_Text_1)\n",
    "travel_ner_out = word_ner_all(travel_chat_preproc)\n",
    "\n",
    "travel_ner_out "
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Next Steps...\n",
    "\n",
    "###  Logic Engine to parse NE"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [],
   "source": [
    "# If no second loaction, ask for start location\n",
    "\n",
    "# If no second date, assume one way\n",
    "\n",
    "# If no money, assume cheapest\n",
    "\n",
    "# If no dates, ask for dates, if not look at today/oneway\n",
    "\n",
    "# If more than 3 locations -> Multicity\n",
    "\n",
    "# Chatterbot\n",
    "# https://chatterbot.readthedocs.io/en/stable/training.html\n",
    "\n",
    "# Start Presentation Tomorrow\n",
    "    # Intro\n",
    "    # Methodology / Challenges\n",
    "    # Tech Stack / Processs\n",
    "    # Demo of Tagging\n",
    "    # Results/Next Steps\n",
    "    \n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
