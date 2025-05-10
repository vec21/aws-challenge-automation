import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

@pytest.fixture
def mock_github():
    with patch('src.cli.Github') as mock:
        yield mock

@pytest.fixture
def mock_repository():
    mock = MagicMock()
    return mock

@pytest.fixture
def mock_pull_request():
    mock = MagicMock()
    mock.number = 1
    mock.title = "Test PR"
    mock.user.login = "testuser"
    mock.created_at = datetime.now(timezone.utc)
    mock.updated_at = datetime.now(timezone.utc)
    mock.comments = 5
    mock.additions = 100
    mock.deletions = 50
    mock.changed_files = 3
    mock.html_url = "https://github.com/test/repo/pull/1"
    mock.state = "open"
    mock.merged = False
    
    # Mock for the get_files method
    mock_file = MagicMock()
    mock_file.filename = "test.py"
    mock_file.changes = 150
    mock_file.patch = "Some code changes\nTODO: Fix this"
    mock.get_files.return_value = [mock_file]
    
    return mock

@pytest.fixture
def mock_pulls_paginated(mock_pull_request):
    mock = MagicMock()
    mock.totalCount = 1
    
    # Make the mock behave like an iterable
    mock.__iter__.return_value = [mock_pull_request]
    
    return mock

@pytest.fixture
def sample_pr_data():
    return [{
        'repo': 'test/repo',
        'number': 1,
        'title': 'Test PR',
        'user': 'testuser',
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
        'comments': 5,
        'additions': 100,
        'deletions': 50,
        'changed_files': 3,
        'url': 'https://github.com/test/repo/pull/1',
        'state': 'open',
        'merged': False,
        'analysis': {}
    }]

@pytest.fixture
def mock_s3_client():
    with patch('boto3.client') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock

@pytest.fixture
def mock_sns_client():
    with patch('boto3.client') as mock:
        mock_client = MagicMock()
        mock_client.create_topic.return_value = {'TopicArn': 'arn:aws:sns:us-east-1:123456789012:test-topic'}
        mock.return_value = mock_client
        yield mock