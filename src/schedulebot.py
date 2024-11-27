import discord  # type: ignore
from discord.ext import commands  # type: ignore
import os
import sys
import shutil
import aiohttp
import json
import asyncio
import traceback
import logging
from discord.ui import Button, View
import requests
from datetime import datetime
import pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))
from functionality.recommend_event import recommend_event
from functionality.AddEvent import add_event  # type: ignore
from functionality.highlights import get_highlight
from functionality.create_event_type import create_event_type
from functionality.FindAvailableTime import find_avaialbleTime
from functionality.delete_event_type import delete_event_type
from functionality.DisplayFreeTime import get_free_time
from functionality.export_file import export_file
from functionality.import_file import import_file
from functionality.Google import connect_google
from functionality.GoogleEvent import get_events
from functionality.Delete_Event import delete_event
from functionality.Edit_event import edit_event
from functionality.shared_functions import (
        add_event_to_file_main,
        fetch_google_events,
        parse_google_event,
        check_passkey,
        create_event_tree,
        read_event_file,
    )
from config import GOOGLE_API_KEY, CLEAR_DATA_PASSKEY

# Configure logging
logger = logging.getLogger('schedulebot')
logger.setLevel(logging.DEBUG)

# Create handlers
debug_handler = logging.FileHandler('debug.log')
debug_handler.setLevel(logging.DEBUG)

error_handler = logging.FileHandler('error.log')
error_handler.setLevel(logging.ERROR)

# Create formatters and add to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(debug_handler)
logger.addHandler(error_handler)

# API URL with the key appended as a query parameter
GOOGLE_AI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_API_KEY}"

# Initialize the bot with appropriate intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure this is enabled in Discord Developer Portal
intents.reactions = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)  # Creates the bot with a command prefix of '!'
bot.remove_command("help")  # Removes the default help command

# ----------------------- Helper Classes -----------------------

class ConfirmDeleteView(View):
    def __init__(self, event_to_delete, ctx, bot_instance):
        super().__init__(timeout=60)
        self.event_to_delete = event_to_delete
        self.ctx = ctx
        self.bot = bot_instance
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message(f"Deleting event '{self.event_to_delete['name']}'...", ephemeral=True)
        success = await delete_event_from_server(self.event_to_delete, self.ctx, self.bot)
        if success:
            await interaction.followup.send(f"Event '{self.event_to_delete['name']}' has been deleted successfully.", ephemeral=True)
        else:
            await interaction.followup.send(f"Failed to delete event '{self.event_to_delete['name']}'.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("Deletion cancelled.", ephemeral=True)
        self.stop()

async def delete_event_from_server(event_to_delete, ctx, bot_instance):
    """
    Deletes the event from Google Calendar and local storage.

    Parameters:
        event_to_delete (dict): Dictionary containing 'id' and 'name' of the event.
        ctx (commands.Context): The context in which the command was invoked.
        bot_instance (commands.Bot): The bot instance.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    try:
        # Connect to Google Calendar
        service = await connect_google(ctx)
        if service is None:
            await ctx.author.send("Failed to connect to Google Calendar.")
            return False

        # Delete the event from Google Calendar
        service.events().delete(calendarId='primary', eventId=event_to_delete['id']).execute()
        logger.info(f"Event '{event_to_delete['name']}' deleted from Google Calendar.")

        # Delete the event from local storage
        success = await delete_event(ctx, bot_instance, event_to_delete)
        if success:
            logger.info(f"Event '{event_to_delete['name']}' deleted from local storage.")
            return True
        else:
            logger.error(f"Failed to delete event '{event_to_delete['name']}' from local storage.")
            return False

    except Exception as e:
        traceback.print_exc()
        logger.error(f"An error occurred while deleting event '{event_to_delete['name']}': {e}", exc_info=True)
        return False

# Helper functions for editing events
async def collect_event_details(ctx):
    """
    Collects new event details from the user.
    """
    channel = ctx.channel

    def check(m):
        return m.author == ctx.author and m.channel == channel

    try:
        await ctx.send("Enter the new event name or type 'skip' to keep it unchanged:")
        name_msg = await bot.wait_for("message", check=check, timeout=60)
        name = name_msg.content if name_msg.content.lower() != 'skip' else None

        await ctx.send("Enter the new start date and time (YYYY-MM-DD HH:MM) or type 'skip':")
        start_msg = await bot.wait_for("message", check=check, timeout=60)
        start = start_msg.content if start_msg.content.lower() != 'skip' else None

        await ctx.send("Enter the new end date and time (YYYY-MM-DD HH:MM) or type 'skip':")
        end_msg = await bot.wait_for("message", check=check, timeout=60)
        end = end_msg.content if end_msg.content.lower() != 'skip' else None

        # Additional fields as needed

        new_event_details = {}
        if name:
            new_event_details['name'] = name
        if start:
            new_event_details['startDateTime'] = start
        if end:
            new_event_details['endDateTime'] = end

        # Validate new details as needed

        return new_event_details
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond.")
        return None
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error collecting event details: {e}", exc_info=True)
        await ctx.send("An error occurred while collecting event details.")
        return None

async def update_event_in_local_storage(user_id, old_event, new_event_details):
    """
    Updates the event in local storage.
    """
    try:
        # Load user's events
        events_file = f'data/{user_id}_events.json'
        if not os.path.exists(events_file):
            return False

        with open(events_file, 'r') as f:
            events = json.load(f)

        # Find and update the event
        for event in events:
            if event['id'] == old_event['id']:
                event.update(new_event_details)
                break

        # Save updated events
        with open(events_file, 'w') as f:
            json.dump(events, f, indent=4)

        return True
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error updating event in local storage: {e}", exc_info=True)
        return False

async def update_event_in_google_calendar(service, old_event, new_event_details):
    """
    Updates the event in Google Calendar.
    """
    try:
        # Fetch the event from Google Calendar
        event = service.events().get(calendarId='primary', eventId=old_event['id']).execute()

        # Update fields
        if 'name' in new_event_details:
            event['summary'] = new_event_details['name']
        if 'startDateTime' in new_event_details:
            event['start']['dateTime'] = new_event_details['startDateTime']
        if 'endDateTime' in new_event_details:
            event['end']['dateTime'] = new_event_details['endDateTime']

        # Update the event in Google Calendar
        updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

        return True
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error updating event in Google Calendar: {e}", exc_info=True)
        return False

def get_user_event_history(user_id):
    """
    Retrieves the event history for a user.
    """
    try:
        events_file = f'data/{user_id}_events.json'
        if not os.path.exists(events_file):
            return []

        with open(events_file, 'r') as f:
            events = json.load(f)

        return events
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error retrieving event history for user {user_id}: {e}", exc_info=True)
        return []

def format_event_history(events):
    """
    Formats the event history for display.
    """
    try:
        if not events:
            return "You have no event history."

        formatted = "📜 **Your Event History:**\n"
        for idx, event in enumerate(events, start=1):
            formatted += f"{idx}. **{event['name']}** from {event['startDateTime']} to {event['endDateTime']}\n"
        return formatted
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error formatting event history: {e}", exc_info=True)
        return "An error occurred while formatting your event history."

# ----------------------- Command Definitions -----------------------

@bot.command()
async def history(ctx):
    """
    Retrieves and displays the history of events attended by the user.
    """
    try:
        user_id = str(ctx.author.id)
        events = get_user_event_history(user_id)
        formatted_history = format_event_history(events)
        await ctx.send(formatted_history)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in history command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while retrieving your event history.")

@bot.command()
# @commands.is_owner()  # Only the bot owner can use this command
async def syncEvents(ctx, passkey: str):
    """
    Synchronizes the next 10 Google Calendar events to local storage after verifying the passkey.
    Usage: !syncEvents <passkey>
    """
    print("check:", passkey, CLEAR_DATA_PASSKEY)
    if not check_passkey(passkey, CLEAR_DATA_PASSKEY):
        await ctx.send("❌ Invalid passkey. Access denied.")
        logger.warning(f"Unauthorized attempt to use syncEvents by {ctx.author} (ID: {ctx.author.id})")
        return

    # Send a confirmation prompt
    await ctx.send("⚠️ **WARNING**: This action will synchronize the next 10 Google Calendar events to local storage. Type `CONFIRM` to proceed.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30)
        if confirmation.content.strip().upper() != 'CONFIRM':
            await ctx.send("Operation cancelled.")
            return
    except asyncio.TimeoutError:
        await ctx.send("⏳ Operation timed out. Please try again.")
        return

    user_id = str(ctx.author.id)

    # Fetch events from Google Calendar
    events, error = await fetch_google_events(ctx, max_results=10)
    if error:
        await ctx.send(error)
        return

    if not events:
        await ctx.send("No upcoming events found in Google Calendar.")
        logger.info(f"No events found in Google Calendar for {ctx.author} (ID: {ctx.author.id})")
        return

    # Ensure the event directory exists
    create_event_tree(user_id)

    # Read existing events from local storage
    local_events = read_event_file(user_id)
    local_event_ids = set()
    if len(local_events) > 1:
        for row in local_events[1:]:
            local_event_ids.add(row[0])  # Assuming the first column is event_id

    # Initialize a counter for new events added
    new_events_count = 0

    for event in events:
        event_id = event.get('id')
        if event_id in local_event_ids:
            # Skip events already in local storage
            continue

        try:
            # Parse the Google event into local format
            local_event = parse_google_event(event)

            # Add event to local storage
            add_event_to_file_main(user_id, local_event)
            new_events_count += 1
        except Exception as e:
            logger.error(f"Error processing event {event_id}: {e}", exc_info=True)
            continue  # Skip this event

    await ctx.send(f"✅ Successfully synchronized {new_events_count} new event(s) from Google Calendar to local storage.")
    logger.info(f"Synchronized {new_events_count} events for {ctx.author} (ID: {ctx.author.id})")

@bot.group(invoke_without_command=True)
async def help(ctx):
    """
    Displays all commands and their descriptions using an embed.
    """
    try:
        await send_help_embed(ctx)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in help command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while displaying help.")

async def send_help_embed(ctx):
    """
    Sends an embed containing all bot commands and their descriptions.
    """
    em = discord.Embed(
        title="📚 ScheduleBot Commands",
        description="Here are all the commands to use ScheduleBot. All commands are prefixed with `!`.",
        color=discord.Color.blue()
    )
    em.add_field(name="!help", value="Displays all commands and their descriptions", inline=False)
    em.add_field(name="!schedule", value="Creates an event", inline=False)
    em.add_field(name="!ConnectGoogle", value="Connect to Google Calendar", inline=False)
    em.add_field(name="!freetime", value="Displays when you are available today", inline=False)
    em.add_field(name="!day", value=(
        "Shows everything on your schedule for a specific date.\n"
        "Format:\n"
        "!day today/tomorrow/yesterday\n"
        "!day 3 (3 days from now)\n"
        "!day -3 (3 days ago)\n"
        "!day 4/20/22 (On Apr 20, 2022)"
    ), inline=False)
    em.add_field(name="!typecreate", value="Creates a new event type", inline=True)
    em.add_field(name="!typedelete", value="Deletes an event type", inline=True)
    em.add_field(name="!exportfile", value="Exports a CSV file of your events", inline=False)
    em.add_field(name="!importfile", value="Import events from a CSV or ICS file", inline=False)
    em.add_field(name="!GoogleEvents", value="Import next 10 events from Google Calendar", inline=False)
    em.add_field(name="!deleteEvent", value="Deletes selected event", inline=False)
    em.add_field(name="!editEvent", value="Edits selected event", inline=False)
    em.add_field(name="!summary", value="Get today's summary", inline=False)
    em.add_field(name="!stop", value="ExitBot (Owner Only)", inline=False)
    em.add_field(name="!recommend <mood>", value="Recommend events based on your mood", inline=False)
    em.add_field(name="!syncEvents [passkey]", value="Synchronizes your Google Calendar events to local storage", inline=False)
    em.add_field(name="!clearData [passkey]", value="Deletes all event data (Owner Only)", inline=False)
    em.add_field(name="!stop [passkey]", value="Stops the bot (Owner Only)", inline=False)
    em.add_field(name="!add <task>", value="Adds a new task to your to-do list", inline=False)
    await ctx.send(embed=em)

@bot.event
async def on_ready():
    """
    Sends a welcome message to all text channels and adds a reaction for users to initiate DM interactions.
    """
    try:
        print(f"We have logged in as {bot.user}")
        channels = bot.get_all_channels()  # Gets all channels the bot has access to

        text_channel_count = 0
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                text_channel_count += 1
                msg = await channel.send(
                "👋 Hello there! I'm **ScheduleBot**, your personal assistant for staying organized and on time. 🕒✨\n\n"
                "If you're ready to start, react to this message with the '🤖' (alarm clock) emoji, and I'll slide into your DMs with all the details!\n"
                "🔒 Just make sure you've enabled DMs from non-friends, so I can reach you easily!"
                )

                await msg.add_reaction("🤖")
        print(f"Sent Welcome Message to {text_channel_count} Text Channel(s)")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in on_ready event: {e}", exc_info=True)

@bot.event
async def on_reaction_add(reaction, user):
    """
    Sends a welcome DM to the user when they react with an alarm clock emoji.
    """
    try:
        emoji = reaction.emoji
        if emoji == "🤖" and not user.bot:
            try:
                await user.send(
                f"👋 Hey there, {user.name}! I'm **ScheduleBot**, your personal assistant for all things scheduling! 📅✨\n\n"
                "Think of me as your trusty sidekick, here to help you stay on top of your plans and make life a little smoother.\n\n"
                "Type `!help` whenever you're ready to explore all the ways I can lend a hand. Let's get organized and make each day count! 🚀"
                )

            except discord.Forbidden:
                print(f"{user.name} ({user.id}) does not have DM permissions set correctly.")
            except Exception as e:
                traceback.print_exc()
                logger.error(f"Error sending DM to {user.name}: {e}", exc_info=True)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in on_reaction_add event: {e}", exc_info=True)

@bot.command()
async def summary(ctx):
    """
    Shows the events planned for the day by the user.
    """
    try:
        await get_highlight(ctx, "today")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in summary command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while retrieving your summary.")

@bot.command(name='ask')
async def ask(ctx, *, user_query: str):
    """
    Interacts with the Google Generative Language API to generate content in response to the user's query.
    Usage: !ask <your question>
    """
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": user_query
                    }
                ]
            }
        ]
    }

    try:
        # Send POST request to the Google API
        response = requests.post(
            GOOGLE_AI_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()

        # Parse the response JSON
        response_data = response.json()

        # Debug: Print the full response data for troubleshooting
        print("Response from Google API:", response_data)

        # Extract the answer from the response
        if "candidates" in response_data:
            answer = response_data["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "I'm not sure how to answer that.")
        else:
            answer = "I'm not sure how to answer that."

        # Check the length of the answer and handle accordingly
        if len(answer) > 2000:
            # Split the response into chunks of 2000 characters
            chunks = [answer[i:i + 2000] for i in range(0, len(answer), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(answer)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 403:
            await ctx.send("Access denied. Please check API key and permissions.")
        else:
            await ctx.send("Sorry, I couldn't process your request.")




@bot.command()
async def schedule(ctx):
    """
    Walks a user through the event creation process.
    """
    try:
        await add_event(ctx, bot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in schedule command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while scheduling your event.")

@bot.command()
async def GoogleEvents(ctx):
    """
    Imports the next 10 events from Google Calendar.
    """
    try:
        await get_events(ctx, bot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in GoogleEvents command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while importing your Google Calendar events.")

@bot.command()
async def find(ctx):
    """
    Walks a user through finding available time slots based on event types.
    """
    try:
        await find_avaialbleTime(ctx, bot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in find command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while finding available time slots.")

@bot.command()
async def day(ctx, arg):
    """
    Shows the events planned for a specific day.

    Parameters:
        arg (str): The date argument provided by the user.
    """
    try:
        await get_highlight(ctx, arg)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in day command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while retrieving events for the specified day.")

@bot.command()
async def exportfile(ctx):
    """
    Sends the user a CSV file containing their scheduled events.
    """
    try:
        await export_file(ctx)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in exportfile command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while exporting your events.")

@bot.command()
async def importfile(ctx):
    """
    Reads a CSV or ICS file containing events submitted by the user and adds those events.
    """
    try:
        await import_file(ctx, bot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in importfile command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while importing your events.")

# Creating new event type
@bot.command()
async def typecreate(ctx):
    """
    Creates a new event type.
    """
    try:
        channel = await ctx.author.create_dm()

        def check(m):
            return m.content is not None and m.channel == channel and m.author == ctx.author

        await channel.send("First, give me the type of your event:")
        try:
            event_msg = await bot.wait_for("message", check=check, timeout=60)  # Waits for user input with a timeout
            event_type = event_msg.content.strip()
            await create_event_type(ctx, bot, event_type)
        except asyncio.TimeoutError:
            await channel.send("You took too long to respond. Please try creating the event type again.")
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in typecreate command: {e}", exc_info=True)
            await channel.send("Sorry, an error occurred while creating the event type.")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in typecreate command setup: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while initiating event type creation.")

# Deleting event
@bot.command()
async def deleteEvent(ctx):
    """
    Deletes an existing event from the user's schedule file and Google Calendar.
    """
    try:
        await delete_event(ctx, bot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in deleteEvent command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while attempting to delete the event.")

# Editing event
@bot.command()
async def editEvent(ctx):
    """
    Edits an existing event.
    """
    try:
        await edit_event(ctx, bot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in editEvent command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while attempting to edit the event.")

@bot.command()
# @commands.is_owner()  # Only the bot owner can use this command
async def clearData(ctx, passkey: str):
    """
    Deletes all event data in the Event Data Directory after verifying the passkey.
    Usage: !clearData <passkey>
    """
    if not check_passkey(passkey, CLEAR_DATA_PASSKEY):
        await ctx.send("❌ Invalid passkey. Access denied.")
        logger.warning(f"Unauthorized attempt to use syncEvents by {ctx.author} (ID: {ctx.author.id})")
        return

    # Send a confirmation prompt
    await ctx.send("⚠️ **WARNING**: This action will permanently delete all event data. Type `CONFIRM` to proceed.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30)
        if confirmation.content.strip().upper() != 'CONFIRM':
            await ctx.send("Operation cancelled.")
            return
    except asyncio.TimeoutError:
        await ctx.send("⏳ Operation timed out. Please try again.")
        return

    # Proceed to delete the Event Data Directory
    event_data_directory = os.path.expanduser('~/Documents/ScheduleBot/Event/')

    try:
        if os.path.exists(event_data_directory):
            # Delete all files in the directory
            for filename in os.listdir(event_data_directory):
                file_path = os.path.join(event_data_directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")
                    await ctx.send(f"❌ Failed to delete {filename}.")
            await ctx.send("✅ All event data has been deleted successfully.")
            logger.info(f"Event data cleared by {ctx.author} (ID: {ctx.author.id})")
        else:
            await ctx.send("ℹ️ Event data directory does not exist.")
            logger.info(f"Event data directory does not exist when {ctx.author} attempted to clear data.")
    except Exception as e:
        logger.error(f"An error occurred while deleting event data: {e}")
        await ctx.send(f"❌ An error occurred while deleting event data: {e}")


# Deleting event type
@bot.command()
async def typedelete(ctx):
    """
    Deletes an event type.
    """
    try:
        channel = await ctx.author.create_dm()

        def check(m):
            return m.content is not None and m.channel == channel and m.author == ctx.author

        await channel.send("Please enter the type of event you want to delete:")
        try:
            type_msg = await bot.wait_for("message", check=check, timeout=60)
            event_type = type_msg.content.strip()
            await delete_event_type(ctx, bot, event_type)
        except asyncio.TimeoutError:
            await channel.send("You took too long to respond. Please try deleting the event type again.")
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in typedelete command: {e}", exc_info=True)
            await channel.send("Sorry, an error occurred while deleting the event type.")
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in typedelete command setup: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while initiating event type deletion.")

# Connecting to Google
@bot.command()
async def ConnectGoogle(ctx):
    """
    Connects the user to Google Calendar.
    """
    try:
        await connect_google(ctx)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in ConnectGoogle command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while connecting to Google Calendar.")

@bot.command()
@commands.is_owner()
async def stop(ctx):
    """
    Stops the bot. Only the bot owner can use this command.
    """
    try:
        await ctx.author.send("Thank you for using ScheduleBot. See you again!")
        await bot.logout()
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in stop command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while trying to stop the bot.")

@bot.command()
async def recommend(ctx, *, mood: str):
    """
    Recommends events based on the user's mood.

    Parameters:
        mood (str): The user's current mood.
    """
    try:
        await recommend_event(ctx, mood)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in recommend command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while generating recommendations based on your mood.")

@bot.command()
async def freetime(ctx):
    """
    Shows the user's free time today according to registered events.
    """
    try:
        await get_free_time(ctx, bot)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error in freetime command: {e}", exc_info=True)
        await ctx.send("Sorry, an error occurred while retrieving your free time.")


# Dictionary to store to-do lists with name, deadline, and description
todo_lists = {}

#Command to add a task with name, deadline (date + time), and description
@bot.command(name="add")
async def add_task(ctx):
    user_id = ctx.author.id
    
    # Ask for the task name
    await ctx.send("Please enter the name of the task:")
    name_msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    name = name_msg.content
    
    # Ask for the task deadline (date + time)
    await ctx.send("Please enter the deadline for the task in the format `YYYY-MM-DD HH:MM` (e.g., 2024-12-01 15:30):")
    deadline_msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    deadline = deadline_msg.content
    
    # Validate and parse the deadline
    try:
        # Try to convert the deadline to a datetime object
        deadline_time = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
    except ValueError:
        await ctx.send("❌ Invalid deadline format! Please use the format `YYYY-MM-DD HH:MM`.")
        return
    
    # Ask for the task description
    await ctx.send("Please enter a description for the task:")
    description_msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    description = description_msg.content
    
    # Store the task in the user's to-do list
    if user_id not in todo_lists:
        todo_lists[user_id] = []
    
    task = {
        "name": name,
        "deadline": deadline_time,  # Store as datetime object
        "description": description
    }
    todo_lists[user_id].append(task)
    
    # Confirm task was added
    await ctx.send(f"✅ Task added: **{name}** (Deadline: {deadline_time.strftime('%Y-%m-%d %H:%M')})\nDescription: {description}")

# Command to view the to-do list with name, deadline, and description
@bot.command(name="list")
async def view_list(ctx):
    user_id = ctx.author.id
    if user_id not in todo_lists or not todo_lists[user_id]:
        await ctx.send("📋 Your to-do list is empty!")
    else:
        tasks = "\n".join([f"{idx+1}. **{task['name']}** (Deadline: {task['deadline'].strftime('%Y-%m-%d %H:%M')})\n  Description: {task['description']}" 
                           for idx, task in enumerate(todo_lists[user_id])])
        await ctx.send(f"📋 **Your To-Do List:**\n{tasks}")

# Command to remove a task
@bot.command(name="remove")
async def remove_task(ctx, task_number: int):
    user_id = ctx.author.id
    if user_id not in todo_lists or not todo_lists[user_id]:
        await ctx.send("❌ Your to-do list is empty!")
    else:
        try:
            removed_task = todo_lists[user_id].pop(task_number - 1)
            await ctx.send(f"🗑️ Task removed: **{removed_task['name']}** (Deadline: {removed_task['deadline'].strftime('%Y-%m-%d %H:%M')})")
        except IndexError:
            await ctx.send("❌ Invalid task number!")

# Command to clear the to-do list
@bot.command(name="clear")
async def clear_list(ctx):
    user_id = ctx.author.id
    if user_id not in todo_lists or not todo_lists[user_id]:
        await ctx.send("🧹 Your to-do list is already empty!")
    else:
        todo_lists[user_id].clear()
        await ctx.send("🧹 Your to-do list has been cleared!")

# ----------------------- Main Execution -----------------------

if __name__ == "__main__":
    from config import TOKEN, GOOGLE_API_KEY  # Ensure you have a config.py with TOKEN,GOOGLE_API_KEY defined

    # Check that the API key is loaded correctly
    if not TOKEN or not GOOGLE_API_KEY:
        raise ValueError(
            "Missing necessary environment variables. Please check your environment variables."
        )

    try:
        bot.run(TOKEN)
    except Exception as e:
        traceback.print_exc()
        logger.critical(f"Failed to run the bot: {e}", exc_info=True)
