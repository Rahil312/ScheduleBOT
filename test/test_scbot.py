import os
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

# Add src directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from schedulebot import add_task, view_list, connect_google

@pytest.fixture
async def ctx():
    mock_ctx = AsyncMock()
    mock_ctx.author.id = 123456789
    mock_ctx.author.create_dm = AsyncMock(return_value=AsyncMock())
    return mock_ctx

@pytest.mark.asyncio
async def test_add_task_success(ctx):
    with patch('schedulebot.service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'htmlLink': 'http://example.com/event',
            'hangoutLink': 'http://example.com/meet'
        }
        
        await add_task(ctx, 'Test Task', 'Test Description', datetime.now())
        assert ctx.send.called
        assert "✅ Task added to Google Calendar!" in ctx.send.call_args[0][0]

@pytest.mark.asyncio
async def test_add_task_failure(ctx):
    with patch('schedulebot.service') as mock_service:
        mock_service.events.return_value.insert.return_value.execute.side_effect = Exception("API Error")
        
        await add_task(ctx, 'Test Task', 'Test Description', datetime.now())
        assert ctx.send.called
        assert "❌ Failed to add the task to Google Calendar." in ctx.send.call_args[0][0]

@pytest.mark.asyncio
async def test_view_list(ctx):
    with patch('schedulebot.get_tasks') as mock_get_tasks:
        mock_get_tasks.return_value = [
            {'name': 'Task 1', 'deadline': datetime.now(), 'description': 'Description 1'},
            {'name': 'Task 2', 'deadline': datetime.now() + timedelta(days=1), 'description': 'Description 2'}
        ]
        
        await view_list(ctx)
        assert ctx.send.called
        assert "Task 1" in ctx.send.call_args[0][0]
        assert "Task 2" in ctx.send.call_args[0][0]

@pytest.mark.asyncio
async def test_connect_google_success(ctx):
    with patch('schedulebot.os.path.exists') as mock_exists, \
         patch('schedulebot.Credentials') as mock_credentials, \
         patch('schedulebot.InstalledAppFlow') as mock_flow, \
         patch('schedulebot.build') as mock_build, \
         patch('schedulebot.open', new_callable=MagicMock) as mock_open:

        # Mock the os.path.exists to return True for all paths
        mock_exists.side_effect = lambda path: True

        # Mock the credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        # Mock the build function
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        service = await connect_google(ctx)
        assert service == mock_service
        assert ctx.author.create_dm.called
        assert ctx.author.create_dm.return_value.send.called

@pytest.mark.asyncio
async def test_connect_google_no_key_file(ctx):
    with patch('schedulebot.os.path.exists') as mock_exists, \
         patch('schedulebot.open', new_callable=MagicMock) as mock_open:

        # Mock the os.path.exists to return False for key file
        mock_exists.side_effect = lambda path: False if 'key.json' in path else True

        service = await connect_google(ctx)
        assert service is None
        assert ctx.author.create_dm.called
        assert ctx.author.create_dm.return_value.send.called

@pytest.mark.asyncio
async def test_connect_google_no_credentials_file(ctx):
    with patch('schedulebot.os.path.exists') as mock_exists, \
         patch('schedulebot.open', new_callable=MagicMock) as mock_open:

        # Mock the os.path.exists to return False for credentials file
        mock_exists.side_effect = lambda path: False if 'credentials.json' in path else True

        service = await connect_google(ctx)
        assert service is None
        assert ctx.author.create_dm.called
        assert ctx.author.create_dm.return_value.send.called

@pytest.mark.asyncio
async def test_connect_google_oauth_flow(ctx):
    with patch('schedulebot.os.path.exists') as mock_exists, \
         patch('schedulebot.Credentials') as mock_credentials, \
         patch('schedulebot.InstalledAppFlow') as mock_flow, \
         patch('schedulebot.build') as mock_build, \
         patch('schedulebot.open', new_callable=MagicMock) as mock_open:

        # Mock the os.path.exists to return True for all paths
        mock_exists.side_effect = lambda path: True

        # Mock the credentials to be invalid and require OAuth flow
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh_token'
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        # Mock the flow
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        # Mock the build function
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        service = await connect_google(ctx)
        assert service == mock_service
        assert ctx.author.create_dm.called
        assert ctx.author.create_dm.return_value.send.called

@pytest.mark.asyncio
async def test_connect_google_oauth_flow_failure(ctx):
    with patch('schedulebot.os.path.exists') as mock_exists, \
         patch('schedulebot.Credentials') as mock_credentials, \
         patch('schedulebot.InstalledAppFlow') as mock_flow, \
         patch('schedulebot.build') as mock_build, \
         patch('schedulebot.open', new_callable=MagicMock) as mock_open:

        # Mock the os.path.exists to return True for all paths
        mock_exists.side_effect = lambda path: True

        # Mock the credentials to be invalid and require OAuth flow
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh_token'
        mock_credentials.from_authorized_user_file.return_value = mock_creds

        # Mock the flow to raise an exception
        mock_flow_instance = MagicMock()
        mock_flow_instance.run_local_server.side_effect = Exception("OAuth Error")
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance

        service = await connect_google(ctx)
        assert service is None
        assert ctx.author.create_dm.called
        assert ctx.author.create_dm.return_value.send.called