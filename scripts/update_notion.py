from typing import Optional
from datetime import datetime, timezone
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")

def update_task_notion(task_id: str, status: Optional[str] = None, effort: Optional[int] = None, priority: Optional[str] = None) -> None:
    """Update a Notion task with the given status, effort, priority, and refresh Updated_at."""
    
    # Build the update payload
    properties = {}
    
    if status is not None:
        properties["Status"] = {"select": {"name": status}}
    
    if effort is not None:
        properties["Effort"] = {"number": effort}
        
    if priority is not None:
        properties["Priority"] = {"select": {"name": priority}}
    
    properties["Updated_at"] = {
        "date": {"start": datetime.now(timezone.utc).isoformat()}
    }
    
    data = {
        "properties": properties,
    }
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    
    try:
        response = requests.patch(f"{NOTION_API_URL}/pages/{task_id}", headers=headers, json=data)
        response.raise_for_status()
        print(f"✅ Successfully updated task {task_id}")
    except Exception as e:
        print(f"❌ Error updating task: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update a Notion task')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('task_id', help='ID of the task to update')
    update_parser.add_argument('--status', help='New status for the task')
    update_parser.add_argument('--priority', help='New priority (Low/Medium/High)')
    update_parser.add_argument('--effort', type=int, help='New effort value')
    update_parser.add_argument('--outcomes', help='New outcomes for the task')
    update_parser.add_argument('--review', help='New review for the task')
    
    args = parser.parse_args()
    
    if args.command == 'update':
        update_task_notion(
            task_id=args.task_id,
            status=args.status,
            priority=args.priority,
            effort=args.effort,
            outcomes=args.outcomes,
            review=args.review
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()