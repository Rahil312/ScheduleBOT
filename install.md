# Installation Instructions for Project Setup

### Get your Discord bot 

 Follow this [tutorial](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) to create your discord bot account.

## Step 1: Clone the Repository from this link
  [Github](https://github.com/Rahil312/ScheduleBOT/tree/Group63_Project3_New_Features)
## Step 2:
  To "login" to your bot through our program, place a file named `config.py` in your src directory with the content:
  
  ```
  TOKEN = ************(your discord bot token)
  ```
  
## Step 3:Intall required packages
  ```
  pip install -r requirements.txt
  ```
  
## Step 4: Connect to Google Cloud
  1. Create a Project 
  2. Setup Billing 
  3. Enable geocoding API and distancematrix API
  4. Generate API key-
      Refer to [this](https://developers.google.com/maps/documentation/geocoding/get-api-key) link for more information about the same.
  5. Store the API key in the following format-
      File name: key.json \
      File Content: 
      ```
      {"key": "your api key here"}
      ```
  6. Key needs to be stored in the json folder.

## Step 5: Run the schedulebot.py
  ```
  python3 schedulebot.py
  ```
  Then your scheduleBot should start working.
  
