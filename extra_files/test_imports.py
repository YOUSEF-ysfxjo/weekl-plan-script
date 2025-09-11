# Test if we can import the module
print("Testing imports...")

try:
    from src.data.notion_task_manager import calculate_completion
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
    print("Current sys.path:")
    import sys
    for p in sys.path:
        print(f"  - {p}")
