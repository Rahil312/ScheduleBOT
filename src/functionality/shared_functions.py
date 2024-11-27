# functionality/shared_functions.py

import sys
import os
import csv
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
import asyncio
from datetime import datetime
from dateutil import parser
from datetime import datetime
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(_file_), ".../")))
from src.Event import Event
from src.functionality.Google import connect_google


logger = logging.getLogger(_name_)


def add_event_to_file_main(user_id, event_data):
    """
    Adds an event to the user's schedule file, encrypting it afterward.
    """
    key = load_key(user_id)
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv")
    decrypt_file(key, event_file_path)

    # Read existing events
    rows = []
    if os.path.exists(event_file_path):
        with open(event_file_path, "r", newline="", encoding='utf-8') as calendar_file:
            csvreader = csv.reader(calendar_file)
            rows = list(csvreader)

    # If the file is empty, add the header
    if not rows:
        rows.append(['eventId', 'name', 'startDateTime', 'endDateTime', 'priority', 'type', 'desc', 'location'])

    # Append the new event
    rows.append([
        event_data['id'],
        event_data['name'],
        event_data['startDateTime'],
        event_data['endDateTime'],
        event_data['priority'],
        event_data['type'],
        event_data['gmeet'],
        event_data['collab'],
        event_data['location'],
        event_data['desc'],
    ])

    # Write the updated events back to the file
    with open(event_file_path, "w", newline="", encoding='utf-8') as calendar_file:
        csvwriter = csv.writer(calendar_file)
        csvwriter.writerows(rows)

    encrypt_file(key, event_file_path)

async def fetch_google_events(ctx, max_results=10):
    """
    Fetches upcoming events from Google Calendar for the authenticated user.

    Parameters:
        ctx (commands.Context): The context from which to get the user and send messages.
        max_results (int): The maximum number of events to fetch.

    Returns:
        Tuple[List[Dict], Optional[str]]: A tuple containing the list of events and an optional error message.
    """
    # Use the updated connect_google function which handles user-specific credentials
    service = await connect_google(ctx)
    if service is None:
        error_message = "Failed to connect to Google Calendar. Please try connecting again using !ConnectGoogle."
        await ctx.send(error_message)
        return None, error_message

    try:
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time in ISO format
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        logger.debug(f"Fetched {len(events)} events for user {ctx.author.id}")
        return events, None
    except Exception as e:
        error_message = f"An error occurred while fetching events: {e}"
        logger.error(error_message)
        await ctx.send("An error occurred while fetching your Google Calendar events.")
        return None, error_message

def parse_google_event(event):
    """
    Parses a Google Calendar event into a dictionary compatible with local storage.

    Input:
        event - The Google Calendar event object.
    Output:
        A dictionary with the event data.
    """
    event_id = event.get('id')
    summary = event.get('summary', 'No Title')
    description = event.get('description', 'None')
    location = event.get('location', 'None')
    gmeet = event.get('gmeet', 'None')
    collab = event.get('attendees', 'None')

    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))

    # Parse dates with time zone awareness
    start_dt = parser.isoparse(start)
    end_dt = parser.isoparse(end)

    # Create the local event object
    local_event = {
        'id': event_id,
        'name': summary,
        'startDateTime': start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        'endDateTime': end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        'priority': 'Medium',  # Default value, adjust as needed
        'type': 'GoogleCalendar',  # Indicate the source
        'gmeet':gmeet,
        'collab':collab,
        'location': location,
        'desc': description,

    }

    return local_event


def check_passkey(provided_passkey, CLEAR_DATA_PASSKEY):
    """
    Checks if the provided passkey matches the one in the environment variable.

    Input:
        provided_passkey - The passkey provided by the user.
    Output:
        True if the passkey matches, False otherwise.
    """
    return provided_passkey == CLEAR_DATA_PASSKEY


def get_event_history(user_id):
    """
    Fetches the event history for the given user ID.
    """
    events = read_event_file(user_id)
    past_events = [
        event for event in events
        if datetime.strptime(event[3], "%Y-%m-%d %H:%M:%S") < datetime.now()
    ]
    return format_event_history(past_events)

def format_event_history(events):
    """
    Formats the list of events into a human-readable string.

    Parameters:
        events (list): A list of event data.

    Returns:
        str: Formatted string of the user's past events.
    """
    if not events:
        return "You have no past events."

    history_str = "Your past events:\n"
    for event in events:
        # Assuming each event is a list with elements in the order:
        # [event_id, event_name, start_date, end_date, priority, event_type, notes, location]
        history_str += f"- {event[1]} (from {event[2]} to {event[3]})\n"

    return history_str

def write_event_file(user_id, rows):
    """
    Writes the event data back to the user's event file, encrypting it afterwards.

    Input:
        user_id - String representing the Discord ID of the user
        rows - List of event rows to write to the file
    Output: None
    """
    key = load_key(user_id)
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv")
    decrypt_file(key, event_file_path)

    with open(event_file_path, "w", newline="", encoding='utf-8') as calendar_file:
        csvwriter = csv.writer(calendar_file)
        csvwriter.writerows(rows)

    encrypt_file(key, event_file_path)


def add_participant_to_event(user_id, event_id):
    # Load events
    events = read_event_file(user_id)
    # Find the event and add the user to the participants
    for event in events:
        if event[0] == event_id:  # Assuming the first column is the event ID
            event.append(user_id)
            break
    # Save the updated events
    write_event_file(user_id, events)

def get_user_event_history(user_id):
    """
    Retrieves the history of events attended by the user.

    Parameters:
        user_id (str): The Discord ID of the user.

    Returns:
        list: A list of past events.
    """
    events = read_event_file(user_id)
    past_events = []

    # Assuming the structure of each event is as follows:
    # [event_id, event_name, start_date, end_date, priority, event_type, notes, location]
    # and the first row of the events file is a header
    for event in events[1:]:
        # Check if the event end date is in the past
        end_date = datetime.strptime(event[3], "%Y-%m-%d %H:%M:%S")
        if end_date < datetime.now():
            past_events.append(event)

    return past_events

def get_user_participation_history(user_id):
    # Load events
    events = read_event_file(user_id)
    # Filter events where the user participated
    participated_events = [event for event in events if user_id in event]
    # Return a formatted list of events
    return [
        f"{event[1]} on {event[2]}" for event in participated_events
    ]  # Adjust indexing based on your CSV structure

def create_type_directory():
    """
    Function: create_type_directory
    Description: Creates ScheduleBot type directory in users Documents folder if it doesn't exist.

    Input: None
    Output: Creates Type folder if it doesn't exist.
    """
    type_dir = os.path.expanduser("~/Documents/ScheduleBot/Type")
    if not os.path.exists(type_dir):
        Path(type_dir).mkdir(parents=True, exist_ok=True)

def create_type_file(user_id):
    """
    Function: create_type_file
    Description: Checks if the event type file exists, and creates it if it doesn't.

    Input:
        user_id - String representing the Discord ID of the user

    Output: Creates the event type file if it doesn't exist.
    """
    type_file_path = os.path.expanduser(
        f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"
    )
    if not os.path.exists(type_file_path):
        with open(type_file_path, "x", newline="") as new_file:
            csvwriter = csv.writer(new_file, delimiter=",")
            csvwriter.writerow(["Event Type", "Start time", "End time"])
        key = check_key(user_id)
        encrypt_file(key, type_file_path)

def create_type_tree(user_id):
    """
    Function: create_type_tree
    Description: Checks if the event type directory and file exists, and creates them if they don't.

    Input:
        user_id - String representing the Discord ID of the user

    Output: Creates the event type folder and file if they don't exist.
    """
    create_type_directory()
    create_type_file(user_id)

def read_type_file(user_id):
    """
    Function: read_type_file
    Description: Reads the event type file for those event types.

    Input:
        user_id - String representing the Discord ID of the user

    Output:
        rows - List of rows.
    """
    key = load_key(user_id)
    type_file_path = os.path.expanduser(
        f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"
    )
    decrypt_file(key, type_file_path)

    # Opens the event type file
    with open(type_file_path, "r") as type_lines:
        type_reader = csv.reader(type_lines, delimiter=",")
        rows = [line for line in type_reader]

    encrypt_file(key, type_file_path)
    return rows

def turn_types_to_string(user_id):
    """
    Function: turn_types_to_string
    Description: Reads the event types file and turns all of them into a formatted string.

    Input:
        user_id - String representing the Discord ID of the user

    Output:
        output - Formatted string of rows in event types file.
    """
    output = ""
    space = [12, 5, 5]
    rows = read_type_file(user_id)
    for line_number, i in enumerate(rows):
        if line_number != 0:
            output += (
                f"{i[0]:<{space[0]}} Preferred range of {i[1]:<{space[1]}} - {i[2]:<{space[2]}}\n"
            )
    return output

def create_event_directory():
    """
    Function: create_event_directory
    Description: Creates ScheduleBot event directory in users Documents folder if it doesn't exist.

    Input: None
    Output: Creates Event folder if it doesn't exist.
    """
    event_dir = os.path.expanduser("~/Documents/ScheduleBot/Event")
    if not os.path.exists(event_dir):
        Path(event_dir).mkdir(parents=True, exist_ok=True)

def create_event_file(user_id):
    """
    Function: create_event_file
    Description: Checks if the calendar file exists, and creates it if it doesn't.

    Input:
        user_id - String representing the Discord ID of the user

    Output: Creates the calendar file if it doesn't exist.
    """
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv")
    if not os.path.exists(event_file_path):
        with open(event_file_path, "x", newline="") as new_file:
            csvwriter = csv.writer(new_file, delimiter=",")
            csvwriter.writerow(
                ["ID", "Name", "Start Date", "End Date", "Priority", "Type", "Notes", "Location"]
            )
        key = check_key(user_id)
        encrypt_file(key, event_file_path)

def create_event_tree(user_id):
    """
    Function: create_event_tree
    Description: Checks if the calendar directory and file exists, and creates them if they don't.

    Input:
        user_id - String representing the Discord ID of the user

    Output: Creates the calendar folder and file if they don't exist.
    """
    create_event_directory()
    create_event_file(user_id)

def read_event_file(user_id):
    """
    Function: read_event_file
    Description: Reads the calendar file and creates a list of rows.

    Input:
        user_id - String representing the Discord ID of the user

    Output:
        rows - List of rows.
    """
    key = load_key(user_id)
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv")
    decrypt_file(key, event_file_path)

    # Opens the current user's csv calendar file
    with open(event_file_path, "r") as calendar_file:
        calendar_reader = csv.reader(calendar_file, delimiter=",")
        rows = [row for row in calendar_reader if len(row) > 0]  # Exclude empty lines

    encrypt_file(key, event_file_path)
    return rows

def add_event_to_file(user_id, current, event_id):
    """
    Function: add_event_to_file
    Description: Adds an event to the calendar file in chronological order.
    Input:
        user_id - String representing the Discord ID of the user
        current - Event object to be added to the calendar
        event_id - String representing the event ID from Google Calendar
    Output: None
    """
    line_number = 0
    rows = read_event_file(user_id)
    # If the file already has events
    if len(rows) > 1:
        for i in rows:
            # Skips check with empty lines
            if len(i) > 0 and line_number != 0:
                # Temporarily turn each line into an Event object to compare with the object we are trying to add
                temp_event = Event(
                    "",
                    datetime.strptime(i[2], "%Y-%m-%d %H:%M:%S"),
                    datetime.strptime(i[3], "%Y-%m-%d %H:%M:%S"),
                    "",
                    "",
                    "",
                    "",
                )
                # If the current Event occurs before the temp Event, insert the current at that position
                if current < temp_event:
                    rows.insert(line_number, [event_id] + current.to_list())
                    break
                # If we have reached the end of the array and not inserted, append the current Event to the array
                if line_number == len(rows) - 1:
                    rows.insert(len(rows), [event_id] + current.to_list())
                    break
            line_number += 1
    else:
        rows.insert(len(rows), [event_id] + current.to_list())
    # Open current user's calendar file for writing
    with open(
        os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv",
        "w",
        newline="",
    ) as calendar_file:
        # Write the column headers and array of rows back to the calendar file
        csvwriter = csv.writer(calendar_file)
        csvwriter.writerows(rows)
    key = load_key(user_id)
    encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Event/" + user_id + ".csv")


def delete_event_from_file(user_id, to_remove):
    rows = read_event_file(user_id)
    type_rows = read_type_file(user_id)
    print("Rows: " + rows._str_())

    for row in rows:
        if to_remove['name'] == row[1]:
            rows.remove(row)

    for type_row in type_rows:
        print("Type Row " + type_row._str_())
        if to_remove['desc'] == str(type_row[0]):
            type_rows.remove(type_row)

    # Open current user's calendar file for writing
    event_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Event/{user_id}.csv")
    with open(event_file_path, "w", newline="") as calendar_file:
        # Write to column headers and array of rows back to the calendar file
        csvwriter = csv.writer(calendar_file)
        csvwriter.writerows(rows)

    key = load_key(user_id)
    encrypt_file(key, event_file_path)

    type_file_path = os.path.expanduser(
        f"~/Documents/ScheduleBot/Type/{user_id}event_types.csv"
    )
    with open(type_file_path, "w", newline="") as type_file:
        csvwriter = csv.writer(type_file, delimiter=",")
        csvwriter.writerows(type_rows)

    key = check_key(user_id)
    encrypt_file(key, type_file_path)

def create_key_directory():
    """
    Function: create_key_directory
    Description: Creates ScheduleBot key directory in users Documents folder if it doesn't exist.

    Input: None
    Output: Creates Key folder if it doesn't exist.
    """
    key_dir = os.path.expanduser("~/Documents/ScheduleBot/Key")
    if not os.path.exists(key_dir):
        Path(key_dir).mkdir(parents=True, exist_ok=True)

def check_key(user_id):
    """
    Function: check_key
    Description: Creates ScheduleBot event key in users Documents folder if it doesn't exist.

    Input:
        user_id - String representing the Discord ID of the user

    Output:
        key - The key for the given user.
    """
    create_key_directory()
    key_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Key/{user_id}.key")
    if not os.path.exists(key_file_path):
        key = write_key(user_id)
    else:
        key = load_key(user_id)
    return key

def write_key(user_id):
    """
    Function: write_key
    Description: Generate the key for the user.

    Input:
        user_id - String representing the Discord ID of the user

    Output:
        key - The written key.
    """
    # Generates a key and saves it into a file
    key = Fernet.generate_key()
    key_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Key/{user_id}.key")
    with open(key_file_path, "wb") as key_file:
        key_file.write(key)
    return key

def load_key(user_id):
    """
    Function: load_key
    Description: Reads the key for the user.

    Input:
        user_id - String representing the Discord ID of the user

    Output:
        key - The loaded key.
    """
    key_file_path = os.path.expanduser(f"~/Documents/ScheduleBot/Key/{user_id}.key")
    with open(key_file_path, "rb") as key_file:
        key = key_file.read()
    return key

def encrypt_file(key, filepath):
    """
    Function: encrypt_file
    Description: Encrypts the given file with the given key.

    Input:
        key - Key to encrypt
        filepath - Filepath to encrypt

    Output: None
    """
    fernet = Fernet(key)
    # Opening the original file to encrypt
    with open(filepath, 'rb') as file:
        original = file.read()

    # Encrypting the file
    encrypted = fernet.encrypt(original)

    # Writing the encrypted data back to the file
    with open(filepath, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

def decrypt_file(key, filepath):
    """
    Function: decrypt_file
    Description: Decrypts the given file with the given key.

    Input:
        key - Key to decrypt
        filepath - Filepath to decrypt

    Output: None
    """
    fernet = Fernet(key)
    # Opening the encrypted file
    with open(filepath, 'rb') as enc_file:
        encrypted = enc_file.read()

    # Decrypting the file
    decrypted = fernet.decrypt(encrypted)

    # Writing the decrypted data back to the file
    with open(filepath, 'wb') as dec_file:
        dec_file.write(decrypted)
