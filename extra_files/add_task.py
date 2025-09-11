#!/usr/bin/env python3
"""
Add a new task to Notion database

Usage:
    python add_task.py "Task Title" [--priority High|Medium|Low] [--effort 1-5] [--status "Not Started"]
"""

import argparse
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data.notion_task_manager import add_task_notion, NOTION_TOKEN, NOTION_DATABASE_ID

def main():
    # Check if NOTION_TOKEN and NOTION_DATABASE_ID are set
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("❌ Error: Required environment variables not set")
        print("Please create a .env file in the project root with:")
        print("NOTION_TOKEN=your_integration_token_here")
        print("NOTION_DATABASE_ID=your_database_id_here")
        return 1

    parser = argparse.ArgumentParser(description='Add a task to Notion')
    parser.add_argument('task', help='Task title/description')
    parser.add_argument('--priority', choices=['High', 'Medium', 'Low'], default='Medium',
                      help='Task priority (default: Medium)')
    parser.add_argument('--effort', type=int, choices=range(1, 6), default=1,
                      help='Effort level 1-5 (default: 1)')
    parser.add_argument('--status', default='Not Started',
                      help='Task status (default: Not Started)')
    parser.add_argument('--outcomes', default='',
                      help='Expected outcomes or notes')
    
    args = parser.parse_args()
    
    try:
        print(f"Adding task: {args.task}")
        print(f"Priority: {args.priority}")
        print(f"Effort: {args.effort}/5")
        print(f"Status: {args.status}")
        if args.outcomes:
            print(f"Outcomes: {args.outcomes}")
        
        result = add_task_notion(
            task=args.task,
            priority=args.priority,
            effort=args.effort,
            status=args.status,
            outcomes=args.outcomes
        )
    
        print("\nResponse from Notion API:")
        print(result)  # This will show the full API response
    
        print("\n✅ Task created successfully!")
        if 'id' in result:
            print(f"Task ID: {result['id']}")
        else:
            print("Note: Task ID not in response. Check your Notion database.")
        
    except Exception as e:
        print(f"\n❌ Error creating task: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1    

if __name__ == "__main__":
    sys.exit(main())
