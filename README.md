# Flight Lookup Chatbot

The goal is to build a travel chat slack bot. A customer will ask the bot in slack a travel related question (flight prices, hotel prices), and aresponse should be returned with flight price, airline and times and for hotels, hotel name andprice per night or total price for the stay.

## Prerequisites

All notebooks are written in Python 3. 

The libraries that are used in this notebook are listed under the `requirements.txt` file. One can simply issue to following command to insure the proper libraries are installed:

```bash
pip3 install -r requirements.txt
```

## Summary of Scripts

### app_hw.py
- Slack bot wrapper, uses functions in chat_bot_response.py to determine response 

### chat_bot_response.py
- Chat bot logic engine, used to determine what to ask the user

### Response_parsing.py
- API requester and parser using RapidAPI

### NER_Attempt_02.py
- Named Entity Recognition Model used to parse the user's response

## Summary of Additional Folders and Files

### database.sqlite3
- Chatbot traning database
 
### /chatbot_env
- environment for files

### /data_ingestion
- scripts for organizing airport names and code data

### /frames
- frames conversational data

### /notebooks
- notebooks used to create app scripts

### /pkl_files
- assorted pkl files

### /Reference
- reference materials

