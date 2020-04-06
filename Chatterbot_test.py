#!/usr/bin/env python
# coding: utf-8

# In[6]:


#%pip install chatterbot-corpus -qq
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import NER_Attempt_03


# In[ ]:


bot = ChatBot(
    'TravelSuzy',
    #storage_adapter='chatterbot.storage.SQLStorageAdapter',
    #database_uri='sqlite:///database.sqlite3'
)

conversation = [
  'Hello'
  'Hi there, where would you like to travel?',
  'I want to go to Italy',
  'For which dates would you like to go?',
  'July 19th to August 12th',
  'And what is your budget for this trip?',
  '2000 dollars',
  'Great, Here are some options:',
]

travel_chat_preproc = word_preproc(conversation)
travel_ner_out = word_ner_all(travel_chat_preproc)

print(travel_ner_out)


# In[ ]:


trainer = ListTrainer(bot)
trainer.train(conversation)

while True:
    try:
        bot_input = bot.get_response(input())
        print(bot_input)

    except(KeyboardInterrupt, EOFError, SystemExit):
        break


# In[4]:


bot.export_for_training('my_export.json')


# In[ ]:




