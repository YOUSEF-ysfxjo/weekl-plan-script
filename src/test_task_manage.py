import os
import sys
import json
from src.task_manage import add_task, update_task, list_tasks, load_tasks

def run_tests():
    """
    Run tests for the task manager
    """
    # Set up test data file path
    test_file = os.path.join(os.path.dirname(__file__), "data", "test_tasks.json")
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    
    # Backup existing file if it exists
    if os.path.exists(test_file):
        backup_file = test_file + ".bak"
        if os.path.exists(backup_file):
            os.remove(backup_file)
        os.rename(test_file, backup_file)
    
    try:
        print("\n" + "="*50)
        print("Starting tests")
        print("="*50)
        
        # Test 1: Add a new task
        print("\n[Test 1] Add a new task")
        task_id = add_task("Complete Python project", "High")
        print(f"✅ Task added successfully with ID: {task_id}")
        print("\nCurrent tasks:")
        list_tasks()
        
        # Test 2: Update the task
        print("\n[Test 2] Update the task")
        result = update_task(task_id, {"status": "In Progress", "effort": 3})
        if result:
            print("✅ Task updated successfully")
            print("\nCurrent tasks:")
            list_tasks()
        else:
            print("❌ Failed to update task")
            
        # Test 3: Update with invalid field
        print("\n[Test 3] Update with invalid field")
        try:
            update_task(task_id, {"invalid_field": "test"})
            print("❌ Should have raised ValueError for invalid field")
        except ValueError as e:
            print(f"✅ Correctly raised error: {e}")
            
        # Test 4: Mark as Done without required fields
        print("\n[Test 4] Try to mark as Done without required fields")
        try:
            update_task(task_id, {"status": "Done"})
            print("❌ Should have required outcomes and review")
        except ValueError as e:
            print(f"✅ Correctly required outcomes and review: {e}")
            
        # Test 5: Mark as Done with all required fields
        print("\n[Test 5] Mark as Done with all required fields")
        result = update_task(task_id, {
            "status": "Done",
            "outcomes": "Completed the task successfully",
            "review": "All tests passed"
        })
        if result:
            print("✅ Task marked as Done successfully")
            print("\nFinal task state:")
            list_tasks()
        else:
            print("❌ Failed to mark task as Done")
            
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        # Restore backup if it exists
        backup_file = test_file + ".bak"
        if os.path.exists(backup_file):
            os.rename(backup_file, test_file)
    
    print("\n" + "="*50)
    print("Tests completed")
    print("="*50)

if __name__ == "__main__":
    run_tests()
