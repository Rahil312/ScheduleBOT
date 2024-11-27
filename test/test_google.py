import os
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))

from src.functionality.Google import connect_google

@pytest.fixture
async def ctx():
    mock_ctx = AsyncMock()
    mock_ctx.author.id = 123456789
    mock_ctx.author.create_dm = AsyncMock(return_value=AsyncMock())
    return mock_ctx

@pytest.mark.asyncio
async def test_connect_google_success(ctx):
    with patch('src.functionality.Google.os.path.exists') as mock_exists, \
         patch('src.functionality.Google.Credentials') as mock_credentials, \
         patch('src.functionality.Google.InstalledAppFlow') as mock_flow, \
         patch('src.functionality.Google.build') as mock_build, \
         patch('src.functionality.Google.open', new_callable=MagicMock) as mock_open:

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
    with patch('src.functionality.Google.os.path.exists') as mock_exists, \
         patch('src.functionality.Google.open', new_callable=MagicMock) as mock_open:

        # Mock the os.path.exists to return False for key file
        mock_exists.side_effect = lambda path: False if 'key.json' in path else True

        service = await connect_google(ctx)
        assert service is None
        assert ctx.author.create_dm.called
        assert ctx.author.create_dm.return_value.send.called

@pytest.mark.asyncio
async def test_connect_google_no_credentials_file(ctx):
    with patch('src.functionality.Google.os.path.exists') as mock_exists, \
         patch('src.functionality.Google.open', new_callable=MagicMock) as mock_open:

        # Mock the os.path.exists to return False for credentials file
        mock_exists.side_effect = lambda path: False if 'credentials.json' in path else True

        service = await connect_google(ctx)
        assert service is None
        assert ctx.author.create_dm.called
        assert ctx.author.create_dm.return_value.send.called

@pytest.mark.asyncio
async def test_connect_google_oauth_flow(ctx):
    with patch('src.functionality.Google.os.path.exists') as mock_exists, \
         patch('src.functionality.Google.Credentials') as mock_credentials, \
         patch('src.functionality.Google.InstalledAppFlow') as mock_flow, \
         patch('src.functionality.Google.build') as mock_build, \
         patch('src.functionality.Google.open', new_callable=MagicMock) as mock_open:

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
    with patch('src.functionality.Google.os.path.exists') as mock_exists, \
         patch('src.functionality.Google.Credentials') as mock_credentials, \
         patch('src.functionality.Google.InstalledAppFlow') as mock_flow, \
         patch('src.functionality.Google.build') as mock_build, \
         patch('src.functionality.Google.open', new_callable=MagicMock) as mock_open:

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
