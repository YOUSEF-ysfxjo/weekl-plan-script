import sys
import os

print("Python version:", sys.version)
print("\nCurrent working directory:", os.getcwd())
print("\nPython path:")
for p in sys.path:
    print(f"  - {p}")

print("\nTrying to import module...")
try:
    from src.data.notion_task_manager import calculate_completion
    print("✅ Successfully imported calculate_completion")
    
    # Test a simple function
    test_tasks = [
        {"status": "Done", "effort": 3, "done_at": "2025-09-01T12:00:00+03:00"},
        {"status": "In Progress", "effort": 2, "done_at": None},
    ]
    result = calculate_completion(test_tasks)
    print(f"✅ calculate_completion result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nCurrent directory contents:")
    for f in os.listdir('.'):
        print(f"  - {f}")
    if os.path.exists('src'):
        print("\nContents of src directory:")
        for f in os.listdir('src'):
            print(f"  - {f}")
