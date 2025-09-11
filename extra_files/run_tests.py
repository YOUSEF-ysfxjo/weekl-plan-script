"""
Test runner for the Notion Task Manager module.
This script can be run directly to execute all tests.
"""
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock, mock_open

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Mock environment variables
os.environ["NOTION_TOKEN"] = "test_token"

# Import the module under test
with patch.dict('os.environ', {'NOTION_TOKEN': 'test_token'}):
    from data.notion_task_manager import (
        calculate_completion, 
        get_top_blockers, 
        get_next_week_goals,
        TIMEZONE,
        get_tasks_notion,
        get_weekly_tasks,
        generate_weekly_report
    )

class TestNotionTaskManager(unittest.TestCase):
    """Test cases for the Notion Task Manager module."""
    
    def test_calculate_completion(self):
        """Test the calculate_completion function."""
        test_tasks = [
            {"status": "Done", "effort": 3, "done_at": "2025-09-01T12:00:00+03:00"},
            {"status": "In Progress", "effort": 2, "done_at": None},
            {"status": "Done", "effort": 1, "done_at": "2025-09-02T12:00:00+03:00"}
        ]
        
        result = calculate_completion(test_tasks)
        self.assertEqual(result, (3, 2, 66.7, 6, 4, 66.7))
    
    def test_get_top_blockers(self):
        """Test the get_top_blockers function."""
        test_tasks = [
            {"task": "Task 1", "status": "Blocked", "priority": "High", "effort": 3},
            {"task": "Task 2", "status": "Blocked", "priority": "Low", "effort": 1},
            {"task": "Task 3", "status": "Done", "priority": "High", "effort": 2},
            {"task": "Task 4", "status": "Blocked", "priority": "Medium", "effort": 2}
        ]
        
        result = get_top_blockers(test_tasks)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["task"], "Task 1")  # Highest priority
        self.assertEqual(result[1]["task"], "Task 4")  # Medium priority
        self.assertEqual(result[2]["task"], "Task 2")  # Low priority

    def test_get_next_week_goals(self):
        """Test the get_next_week_goals function."""
        test_tasks = [
            {"task": "Task 1", "status": "Not Started", "priority": "High", "effort": 3},
            {"task": "Task 2", "status": "In Progress", "priority": "Medium", "effort": 2},
            {"task": "Task 3", "status": "Done", "priority": "High", "effort": 1},
            {"task": "Task 4", "status": "Not Started", "priority": "Low", "effort": 2}
        ]
        
        result = get_next_week_goals(test_tasks)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["task"], "Task 1")  # High priority, high effort
        self.assertEqual(result[1]["task"], "Task 2")  # In progress, medium priority
        self.assertEqual(result[2]["task"], "Task 4")  # Low priority
    
    @patch('data.notion_task_manager.requests.post')
    def test_get_tasks_notion(self, mock_post):
        """Test the get_tasks_notion function with mocked API response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "test_id",
                    "properties": {
                        "Task": {"title": [{"plain_text": "Test Task"}]},
                        "Status": {"select": {"name": "In Progress"}},
                        "Priority": {"select": {"name": "High"}},
                        "Effort": {"number": 3},
                        "Outcomes": {"rich_text": [{"plain_text": "Test outcomes"}]},
                        "Review": {"rich_text": [{"plain_text": "Test review"}]},
                        "Created_at": {"date": {"start": "2025-09-01T10:00:00+03:00"}},
                        "Updated_at": {"date": {"start": "2025-09-01T12:00:00+03:00"}},
                        "Done_at": {"date": None}
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Call the function
        result = get_tasks_notion("test_db_id")
        
        # Verify the result
        self.assertEqual(len(result["tasks"]), 1)
        self.assertEqual(result["tasks"][0]["task"], "Test Task")
        self.assertEqual(result["tasks"][0]["status"], "In Progress")
        self.assertEqual(result["tasks"][0]["priority"], "High")
    
    @patch('data.notion_task_manager.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('data.notion_task_manager.get_weekly_tasks')
    @patch('data.notion_task_manager.md.markdownFromFile')
    def test_generate_weekly_report(self, mock_markdown, mock_get_weekly_tasks, mock_open_file, mock_makedirs):
        """Test the generate_weekly_report function."""
        # Setup mock data
        mock_get_weekly_tasks.return_value = [
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
        
        # Call the function
        generate_weekly_report("test_db_id")
        
        # Verify the function created the reports directory
        mock_makedirs.assert_called_once_with("reports", exist_ok=True)
        
        # Verify the markdown file was written
        mock_open_file.assert_called()
        
        # Verify markdown conversion was called
        mock_markdown.assert_called_once()

if __name__ == "__main__":
    print("Starting tests...\n")
    
    # Run the tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestNotionTaskManager)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print a summary
    print("\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
