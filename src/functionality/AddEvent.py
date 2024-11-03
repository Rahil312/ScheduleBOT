"""
Add Event Module

This module handles the addition of events through a Discord bot interface. It interacts with
Google Calendar API to create, manage, and delete events based on user input.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from functionality.shared_functions import (
    create_event_tree,
    create_type_tree,
    add_event_to_file,
    turn_types_to_string,
)
from functionality.create_event_type import create_event_type
from functionality.distance import get_distance
from parse.match import parse_period, parse_period24

from Event.Event import Event

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import asyncio  # Added for potential asynchronous operations

# Constants
SCOPES = ['https://www.googleapis.com/auth/calendar']


def check_complete(start: bool, start_date: datetime, end: bool, end_date: datetime, array: list) -> bool:
    """
    Check if both start and end dates are complete.

    Args:
        start (bool): Indicates if the start date is complete.
        start_date (datetime): The start date.
        end (bool): Indicates if the end date is complete.
        end_date (datetime): The end date.
        array (list): List to append dates if complete.

    Returns:
        bool: True if both dates are complete, else False.
    """
    if start and end:
        print("Both date objects created")
        array.extend([start_date, end_date])
        return True
    return False


async def add_event(ctx, client):
    """
    Walks a user through the event creation process.

    Args:
        ctx: Discord context window.
        client: Discord bot user.

    Outputs:
        - A new event added to the user's calendar file.
        - A message sent to the context saying an event was successfully created.
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    event_array = []

    await channel.send("Let's add an event!\nWhat is the name of your event?:")
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_array.append(event_msg.content.strip())

    await channel.send(
        "Now give me the start & end dates for your event. "
        "You can use 12-hour formatting or 24-hour formatting.\n\n"
        "Here is the format you should follow (Start is first, end is second):\n"
        "mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm (12-hour formatting)\n"
        "Or mm/dd/yy hh:mm mm/dd/yy hh:mm (24-hour formatting)"
    )

    event_dates = False
    attempt_flag = 0  # To track the number of attempts

    while not event_dates:
        msg_content = ""
        start_complete = False
        end_complete = False

        event_msg = await client.wait_for("message", check=check)
        msg_content = event_msg.content.strip()

        if any(period in msg_content.lower() for period in ["am", "pm"]):
            try:
                parse_result = parse_period(msg_content)
                start_complete = True
            except ValueError as e:
                await channel.send(
                    f"Looks like {e}. Please re-enter your dates.\n"
                    "Here is the format you should follow (Start is first, end is second):\n"
                    "mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm"
                )
                continue

            start_date, end_date = parse_result

            if check_complete(start_complete, start_date, True, end_date, event_array):
                event_dates = True
            else:
                await channel.send(
                    "Make sure you follow this format(Start is first, end is second): "
                    "mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm"
                )
        else:
            try:
                parse_result = parse_period24(msg_content)
                start_complete = True
            except ValueError as e:
                await channel.send(
                    f"Looks like {e}. Please re-enter your dates.\n"
                    "Here is the format you should follow (Start is first, end is second):\n"
                    "mm/dd/yy hh:mm mm/dd/yy hh:mm"
                )
                attempt_flag += 1
                if attempt_flag > 3:
                    await channel.send("Unable to create event due to incorrect time format.")
                    return
                continue

            start_date, end_date = parse_result

            if check_complete(start_complete, start_date, True, end_date, event_array):
                event_dates = True
            else:
                attempt_flag += 1
                if attempt_flag > 3:
                    await channel.send("Unable to create event due to incorrect time format.")
                    return
                await channel.send(
                    "Make sure you follow this format(Start is first, end is second): "
                    "mm/dd/yy hh:mm mm/dd/yy hh:mm"
                )

    # Gathering event priority
    event_priority_set = False
    while not event_priority_set:
        await channel.send(
            "How important is this event? Enter a number between 1-5.\n\n"
            "5 - Highest priority.\n"
            "4 - High priority.\n"
            "3 - Medium priority.\n"
            "2 - Low priority.\n"
            "1 - Lowest priority."
        )

        event_msg = await client.wait_for("message", check=check)
        priority = event_msg.content.strip()

        if priority.isdigit() and 1 <= int(priority) <= 5:
            event_array.append(priority)
            event_priority_set = True
        else:
            await channel.send("Please enter a number between 1-5.\n")

    # Creating event type
    create_type_tree(str(ctx.author.id))
    output = turn_types_to_string(str(ctx.author.id))
    await channel.send(
        f"Tell me what type of event this is. Here is a list of event types I currently know:\n{output}"
    )
    event_msg = await client.wait_for("message", check=check)
    event_type = event_msg.content.strip()
    await create_event_type(ctx, client, event_type)
    event_array.append(event_type)

    # Gathering event location
    await channel.send("What is the location of the event? (Type 'None' for no location)")
    event_msg = await client.wait_for("message", check=check)
    location = event_msg.content.strip()
    event_array.append(location)
    destination = location

    if destination.lower() != 'none':
        await channel.send("Do you want to block travel time for this event? (Yes/No)")
        event_msg = await client.wait_for("message", check=check)
        travel_flag = event_msg.content.strip().lower()

        if travel_flag == 'yes':
            await channel.send(
                "Enter exact string out of the following modes: [DRIVING, WALKING, BICYCLING, TRANSIT]"
            )
            event_msg = await client.wait_for("message", check=check)
            mode = event_msg.content.strip().upper()

            if mode not in ["DRIVING", "WALKING", "BICYCLING", "TRANSIT"]:
                await channel.send("Invalid mode entered. Please try adding travel time again.")
            else:
                await channel.send("Enter source address:")
                event_msg = await client.wait_for("message", check=check)
                source = event_msg.content.strip()

                try:
                    travel_time, maps_link = get_distance(destination, source, mode)
                    end_date = event_array[1]
                    start_time = end_date - timedelta(seconds=travel_time)

                    travel_event = Event("Travel", start_time, end_date, "1", "", "", "")
                    await channel.send("Your Travel event was successfully created!")
                    await channel.send(f"Here is your Google Maps link for navigation: {maps_link}")

                    create_event_tree(str(ctx.author.id))
                    add_event_to_file(str(ctx.author.id), travel_event)
                except Exception as e:
                    await channel.send(f"Failed to add travel time: {e}")

    # Gathering additional description
    await channel.send("Any additional description you want me to add about the event? If not, enter 'done'")
    event_msg = await client.wait_for("message", check=check)
    additional_description = event_msg.content.strip()

    if additional_description.lower() == "done":
        event_array.append("")
    else:
        event_array.append(additional_description)

    # Adding to Google Calendar
    try:
        creds = None
        token_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "json", 
            "token.json"
        )

        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        else:
            await channel.send("You are not logged into Google. Please login using the !ConnectGoogle command.")
            return

        service = build('calendar', 'v3', credentials=creds)
        print("Token found and service built.")

        new_event = {
            'summary': event_array[0],
            'location': event_array[-2],
            'description': event_array[-1],
            'start': {
                'dateTime': event_array[1].strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/New_York'
            },
            'end': {
                'dateTime': event_array[2].strftime("%Y-%m-%dT%H:%M:%S"),
                'timeZone': 'America/New_York'
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 60},
                    {'method': 'popup', 'minutes': 5},
                ]
            }
        }

        event = service.events().insert(calendarId='primary', body=new_event).execute()
        print(f'Event created: {event.get("htmlLink")}')
        await channel.send(f'Event created: {event.get("htmlLink")}')

        # Creating Event object and saving to file
        try:
            current_event = Event(
                event_array[0],
                event_array[1],
                event_array[2],
                event_array[3],
                event_array[4],
                event_array[6],
                event_array[5]
            )
            await channel.send("Your event was successfully created!")
            create_event_tree(str(ctx.author.id))
            add_event_to_file(str(ctx.author.id), current_event)
        except Exception as e:
            print(e)
            await channel.send(
                "There was an error in creating your event. Make sure your formatting is correct and try creating the event again."
            )
    except HttpError as http_err:
        await channel.send(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(e)
        await channel.send(
            "There was an error in creating your event. Make sure your formatting is correct and try creating the event again."
        )
