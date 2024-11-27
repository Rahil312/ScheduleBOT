import sys
import os
import asyncio
import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta

# Add project root to sys.path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))

from src.functionality.AddEvent import add_event

@pytest.fixture
async def bot(event_loop):
    intents = discord.Intents.default()
    intents.members = True
    b = commands.Bot(command_prefix="!", intents=intents)

    @b.command()
    async def test_add(ctx):
        await add_event(ctx, b)  # Call add_event directly without threading

    await dpytest.configure(b)  # Configure dpytest with the bot
    return b

@pytest.mark.asyncio
async def test_add_event_success(bot):
    with patch('src.functionality.AddEvent.service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'htmlLink': 'http://example.com/event',
            'hangoutLink': 'http://example.com/meet'
        }
        
        await dpytest.message("!test_add")
        assert dpytest.verify().message().content("Your event was successfully created!")
        assert dpytest.verify().message().content("Event link: http://example.com/event")

@pytest.mark.asyncio
async def test_add_event_failure(bot):
    with patch('src.functionality.AddEvent.service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.side_effect = Exception("API Error")
        
        await dpytest.message("!test_add")
        assert dpytest.verify().message().content("There was an error in creating your event. Please check your inputs and try again.")

@pytest.mark.asyncio
async def test_add_event_invalid_date(bot):
    with patch('src.functionality.AddEvent.datetime') as mock_datetime:
        mock_datetime.strptime.side_effect = ValueError("Invalid date format")
        
        await dpytest.message("!test_add")
        assert dpytest.verify().message().content("There was an error in creating your event. Please check your inputs and try again.")

@pytest.mark.asyncio
async def test_add_event_with_gmeet(bot):
    with patch('src.functionality.AddEvent.service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'htmlLink': 'http://example.com/event',
            'hangoutLink': 'http://example.com/meet'
        }
        
        await dpytest.message("!test_add")
        await dpytest.message("gmeet")
        assert dpytest.verify().message().content("Your event was successfully created!")
        assert dpytest.verify().message().content("Event link: http://example.com/event")
        assert dpytest.verify().message().content("Google Meet link: http://example.com/meet")

@pytest.mark.asyncio
async def test_add_event_with_collaborators(bot):
    with patch('src.functionality.AddEvent.service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'htmlLink': 'http://example.com/event',
            'hangoutLink': 'http://example.com/meet'
        }
        
        await dpytest.message("!test_add")
        await dpytest.message("collaborator1@gmail.com, collaborator2@gmail.com")
        assert dpytest.verify().message().content("Collaborators added: collaborator1@gmail.com, collaborator2@gmail.com")
        assert dpytest.verify().message().content("Your event was successfully created!")
        assert dpytest.verify().message().content("Event link: http://example.com/event")

@pytest.mark.asyncio
async def test_add_event_no_collaborators(bot):
    with patch('src.functionality.AddEvent.service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'htmlLink': 'http://example.com/event',
            'hangoutLink': 'http://example.com/meet'
        }
        
        await dpytest.message("!test_add")
        await dpytest.message("None")
        assert dpytest.verify().message().content("No collaborators added.")
        assert dpytest.verify().message().content("Your event was successfully created!")
        assert dpytest.verify().message().content("Event link: http://example.com/event")