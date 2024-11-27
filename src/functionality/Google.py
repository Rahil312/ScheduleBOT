# functionality/google.py

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs
logger = logging.getLogger(_name_)

async def connect_google(ctx):
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None

    # Define the directory where JSON files are stored
    base_dir = os.path.dirname(os.path.abspath(_file_)) 
    print(base_dir)     # ...\src
    logger.debug(f"Base directory: {base_dir}")
    parent_dir = os.path.dirname(base_dir)                     # ...\SEProj-ScheduleBot-main
    json_dir = os.path.join(parent_dir, "json")               # ...\json
    logger.debug(f"JSON directory: {json_dir}")

    # Paths to required JSON files and user-specific token
    user_id = str(ctx.author.id)  # Use Discord user ID to isolate credentials
    token_file_path = os.path.join(json_dir, "tokens", f"{user_id}_token.json")  # user-specific token path

    # Create tokens directory if it does not exist
    tokens_dir = os.path.join(json_dir, "tokens")
    if not os.path.exists(tokens_dir):
        os.makedirs(tokens_dir)
        logger.debug(f"Created tokens directory at {tokens_dir}")

    # Paths for shared files
    cred_file_path = os.path.join(json_dir, "credentials.json")
    key_data_path = os.path.join(json_dir, "key.json")

    # Send DM to user
    channel = await ctx.author.create_dm()
    await channel.send("We will now connect to Google Calendar.")

    # Check if API Key file exists
    if not os.path.exists(key_data_path):
        error_message = "API Key file does not exist. Please refer to the README to add the key and restart the program."
        logger.error(error_message)
        await channel.send(error_message)
        return None

    # Check if credentials.json exists
    if not os.path.exists(cred_file_path):
        error_message = "OAuth credentials file does not exist. Please set up OAuth credentials and restart the program."
        logger.error(error_message)
        await channel.send(error_message)
        return None

    # Load existing user-specific credentials if available
    if os.path.exists(token_file_path):
        try:
            creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)
            logger.info(f"Credentials loaded from {token_file_path}.")
        except Exception as e:
            logger.error(f"Error loading credentials from {token_file_path}: {e}")
            creds = None

    # If no valid credentials, initiate OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Credentials refreshed.")
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None

        if not creds or not creds.valid:
            await channel.send("Please check the tab in your browser for authentication.")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(cred_file_path, SCOPES)
                creds = flow.run_local_server(port=8080)  # Fixed port
                logger.info("OAuth flow completed successfully.")
                await channel.send("Login Successful.")
            except Exception as e:
                error_message = f"OAuth flow failed: {e}"
                logger.error(error_message)
                await channel.send(error_message)
                return None

            # Save the user-specific credentials for the next run
            try:
                with open(token_file_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                logger.info(f"Credentials saved to {token_file_path}.")
            except Exception as e:
                logger.error(f"Error saving credentials: {e}")
                await channel.send("Failed to save credentials.")
                return None

    await channel.send("You are now connected to Google.")
    try:
        service = build('calendar', 'v3', credentials=creds)
        logger.debug("Google Calendar service built successfully.")
        return service  # Return the service object
    except Exception as e:
        logger.error(f"Error building Google Calendar service: {e}")
        await channel.send("Failed to build Google Calendar service.")
        return None
