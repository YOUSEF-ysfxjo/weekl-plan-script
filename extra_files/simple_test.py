import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    print("Trying to import calculate_completion...")
    from data.notion_task_manager import calculate_completion
    print("✅ Successfully imported calculate_completion")
    
    # Test the function
    test_tasks = [
        {"status": "Done", "effort": 3, "done_at": "2025-09-01T12:00:00+03:00"},
        {"status": "In Progress", "effort": 2, "done_at": None},
    ]
    result = calculate_completion(test_tasks)
    print(f"✅ calculate_completion result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nCurrent directory:", os.getcwd())
    print("\nDirectory contents:")
    for f in os.listdir('.'):
        print(f"- {f}")
    
    if os.path.exists('src'):
        print("\nContents of src directory:")
        for f in os.listdir('src'):
            print(f"- {f}")
            if f == 'data' and os.path.isdir('src/data'):
                print("  Contents of data directory:")
                for df in os.listdir('src/data'):
                    print(f"  - {df}")
