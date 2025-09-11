import os
import sys
import json
import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock

# Import all functions we want to test
from src.task_manage import (
    add_task, update_task, list_tasks, load_tasks, save_tasks,
    get_weekly_tasks, calculate_completion, get_top_blockers, 
    get_next_week_goals, generate_weekly_report,
    TIMEZONE, START_DATE, week_start, end_of_week, week_number, week_range
)

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a test tasks file
        self.test_file = "sample.json"
        with open(self.test_file, 'w') as f:
            json.dump({"tasks": [], "last_updated": datetime.now(TIMEZONE).isoformat()}, f)
    
    def tearDown(self):
        """Clean up after each test."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_add_task(self):
        """Test adding a new task."""
        task_id = add_task("Test task", "Medium", 2)
        self.assertIsNotNone(task_id)
        
        tasks = load_tasks()
        self.assertEqual(len(tasks["tasks"]), 1)
        self.assertEqual(tasks["tasks"][0]["task"], "Test task")
        self.assertEqual(tasks["tasks"][0]["priority"], "Medium")
        self.assertEqual(tasks["tasks"][0]["effort"], 2)
        self.assertEqual(tasks["tasks"][0]["status"], "Not Started")
    
    def test_update_task(self):
        """Test updating a task."""
        task_id = add_task("Test task", "Medium")
        result = update_task(task_id, {"status": "In Progress", "effort": 3})
        self.assertTrue(result)
        
        tasks = load_tasks()
        task = next(t for t in tasks["tasks"] if t["id"] == task_id)
        self.assertEqual(task["status"], "In Progress")
        self.assertEqual(task["effort"], 3)
    
    def test_mark_task_done_without_required_fields(self):
        """Test marking a task as Done without required fields."""
        task_id = add_task("Test task", "High")
        with self.assertRaises(ValueError) as context:
            update_task(task_id, {"status": "Done"})
        self.assertIn("Outcomes and review are required", str(context.exception))
    
    def test_mark_task_done_with_required_fields(self):
        """Test marking a task as Done with all required fields."""
        task_id = add_task("Test task", "High", outcomes="Task in progress", review="Initial review")
        result = update_task(task_id, {
            "status": "Done",
            "outcomes": "Task completed successfully",
            "review": "All tests passed"
        })
        self.assertTrue(result)
        
        tasks = load_tasks()
        task = next(t for t in tasks["tasks"] if t["id"] == task_id)
        self.assertEqual(task["status"], "Done")
        self.assertIsNotNone(task.get("done_at"))
    
    def test_get_weekly_tasks(self):
        """Test getting tasks for the current week."""
        # Add tasks with different timestamps
        now = datetime.now(TIMEZONE)
        last_week = now - timedelta(days=7)
        
        # This task should be included (current week)
        task1_id = add_task("Current week task", "High")
        
        # This task should be included (current week)
        task2_id = add_task("Another current week task", "Medium", outcomes="Task done", review="Good work")
        
        # Update task2 to appear as if it was done this week
        update_task(task2_id, {
            "status": "Done",
            "outcomes": "Task completed successfully",
            "review": "All tests passed"
        })
        
        weekly_tasks = get_weekly_tasks()
        self.assertGreaterEqual(len(weekly_tasks), 1)
        task_ids = [t["id"] for t in weekly_tasks]
        self.assertIn(task1_id, task_ids)
        self.assertIn(task2_id, task_ids)
    
    def test_calculate_completion(self):
        """Test completion calculation."""
        # Add some test tasks
        task1_id = add_task("Task 1", "High", 3, "Completed successfully", "All tests passed")
        task2_id = add_task("Task 2", "Medium", 2)
        task3_id = add_task("Task 3", "Low", 1)
        
        # Mark one task as done with required fields
        update_task(task1_id, {
            "status": "Done",
            "outcomes": "Task completed successfully",
            "review": "All tests passed"
        })
        
        weekly_tasks = get_weekly_tasks()
        result = calculate_completion(weekly_tasks)
        
        # Verify the calculations
        self.assertEqual(result[0], 3)  # total tasks
        self.assertEqual(result[1], 1)  # done count
        self.assertAlmostEqual(result[2], 33.3, places=1)  # done percent
        self.assertEqual(result[3], 6)  # total effort
        self.assertEqual(result[4], 3)  # done effort
        self.assertAlmostEqual(result[5], 50.0, places=1)  # effort percent
    
    @patch('builtins.print')
    def test_list_tasks(self, mock_print):
        """Test listing tasks."""
        add_task("Test task", "High")
        list_tasks()
        
        # Verify something was printed
        self.assertTrue(mock_print.called)
        output = '\n'.join([call[0][0] for call in mock_print.call_args_list])
        self.assertIn("Test task", output)
        self.assertIn("High", output)
    
    @patch('src.task_manage.datetime')
    @patch('src.task_manage.md.markdownFromFile')
    def test_generate_weekly_report(self, mock_markdown, mock_datetime):
        """Test generating a weekly report."""
        # Mock datetime to control the week calculation
        mock_now = datetime(2025, 9, 3, 12, 0, 0, tzinfo=TIMEZONE)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        # Add test data
        add_task("Completed task", "High", 3, "Done", "Good", "Done")
        add_task("Blocked task", "Medium", 2, "", "", "Blocked")
        add_task("In Progress task", "Low", 1, "", "", "In Progress")
        
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Generate report
        generate_weekly_report()
        
        # Verify markdown was called
        self.assertTrue(mock_markdown.called)
        
        # Check if report file was created
        self.assertTrue(os.path.exists('reports/weekly.md'))
        
        # Clean up
        if os.path.exists('reports/weekly.md'):
            os.remove('reports/weekly.md')
        if os.path.exists('reports/weekly.html'):
            os.remove('reports/weekly.html')


if __name__ == "__main__":
    unittest.main()
