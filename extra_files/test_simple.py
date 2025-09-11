import sys
import os

def main():
    print("Python version:", sys.version)
    print("\nCurrent working directory:", os.getcwd())
    print("\nPython path:")
    for p in sys.path:
        print(f"  - {p}")
    
    print("\nTrying to import modules...")
    try:
        import unittest
        from unittest.mock import patch, MagicMock
        print("✅ unittest and mock imported successfully")
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
    
    print("\nEnvironment variables:")
    for key in ['NOTION_TOKEN', 'PYTHONPATH']:
        print(f"{key}: {os.environ.get(key, 'Not set')}")

if __name__ == "__main__":
    main()
