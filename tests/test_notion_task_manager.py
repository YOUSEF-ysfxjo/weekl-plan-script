import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module under test
from src.data.notion_task_manager import calculate_completion, get_top_blockers, get_next_week_goals

# Test data
SAMPLE_TASKS = {
    "results": [
        {
            "id": "1",
            "properties": {
                "Task": {"title": [{"plain_text": "Test Task 1"}]},
                "Status": {"select": {"name": "Done"}},
                "Priority": {"select": {"name": "High"}},
                "Effort": {"number": 3},
                "Outcomes": {"rich_text": [{"plain_text": "Outcome 1"}]},
                "Review": {"rich_text": [{"plain_text": "Review 1"}]},
                "Created_at": {"date": {"start": "2025-09-01T10:00:00+03:00"}},
                "Updated_at": {"date": {"start": "2025-09-01T12:00:00+03:00"}},
                "Done_at": {"date": {"start": "2025-09-01T12:00:00+03:00"}}
            }
        },
        {
            "id": "2",
            "properties": {
                "Task": {"title": [{"plain_text": "Test Task 2"}]},
                "Status": {"select": {"name": "Blocked"}},
                "Priority": {"select": {"name": "Medium"}},
                "Effort": {"number": 2},
                "Outcomes": {"rich_text": [{"plain_text": ""}]},
                "Review": {"rich_text": [{"plain_text": ""}]},
                "Created_at": {"date": {"start": "2025-09-02T10:00:00+03:00"}},
                "Updated_at": {"date": {"start": "2025-09-02T12:00:00+03:00"}},
                "Done_at": {"date": None}
            }
        }
    ]
}

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("NOTION_TOKEN", "test_token")

@pytest.fixture
def mock_requests_get():
    with patch('requests.post') as mock_post:
        yield mock_post

@pytest.fixture
def mock_datetime(monkeypatch):
    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2025, 9, 6, 12, 0, 0, tzinfo=tz or timezone.utc)
    
    monkeypatch.setattr('datetime.datetime', MockDateTime)
    return MockDateTime

def test_get_tasks_notion(mock_requests_get, mock_env):
    # Setup mock
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_TASKS
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response
    
    # Call function
    result = get_tasks_notion("test_db_id")
    
    # Assertions
    assert len(result["tasks"]) == 2
    assert result["tasks"][0]["task"] == "Test Task 1"
    assert result["tasks"][1]["status"] == "Blocked"
    assert result["tasks"][0]["priority"] == "High"


def test_calculate_completion():
    test_tasks = [
        {"status": "Done", "effort": 3, "done_at": "2025-09-01T12:00:00+03:00"},
        {"status": "In Progress", "effort": 2, "done_at": None},
        {"status": "Done", "effort": 1, "done_at": "2025-09-02T12:00:00+03:00"}
    ]
    
    result = calculate_completion(test_tasks)
    assert result == (3, 2, 66.7, 6, 4, 66.7)

def test_get_top_blockers():
    test_tasks = [
        {"task": "Task 1", "status": "Blocked", "priority": "High", "effort": 3},
        {"task": "Task 2", "status": "Blocked", "priority": "Low", "effort": 1},
        {"task": "Task 3", "status": "Done", "priority": "High", "effort": 2},
        {"task": "Task 4", "status": "Blocked", "priority": "Medium", "effort": 2}
    ]
    
    result = get_top_blockers(test_tasks)
    assert len(result) == 3
    assert result[0]["task"] == "Task 1"  # Highest priority
    assert result[1]["task"] == "Task 4"  # Medium priority
    assert result[2]["task"] == "Task 2"  # Low priority

@patch('builtins.open')
@patch('os.makedirs')
@patch('src.data.notion_task_manager.get_weekly_tasks')
def test_generate_weekly_report(mock_get_weekly_tasks, mock_makedirs, mock_open, tmp_path):
    # Setup test data
    test_tasks = [
        {
            "task": "Test Task 1", 
            "status": "Done", 
            "priority": "High", 
            "effort": 3,
            "done_at": "2025-09-01T12:00:00+03:00"
        },
        {
            "task": "Test Task 2", 
            "status": "Blocked", 
            "priority": "Medium", 
            "effort": 2,
            "done_at": None
        }
    ]
    mock_get_weekly_tasks.return_value = test_tasks
    
    # Call function
    generate_weekly_report("test_db_id")
    
    # Verify files were created
    mock_makedirs.assert_called_once_with("reports", exist_ok=True)
    assert mock_open.call_count == 2  # Called once for .md and once for .html

# Add more test cases for other functions...
