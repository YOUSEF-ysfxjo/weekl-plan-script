import os
import sys
import argparse
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data.notion_task_manager import get_tasks_notion

def list_tasks(database_id: str) -> None:
    from datetime import datetime, timezone, timedelta
    
    tasks = get_tasks_notion(database_id)

    if not tasks["tasks"]:
        print("No tasks available")
        return

    for task in tasks["tasks"]:
        print("\n" + "=" * 50)
        print(f"Task: {task['task']}")
        print("-" * 30)
        print(f"ID: {task['id']}")
        print(f"Status: {task['status']}")
        print(f"Priority: {task['priority']}")
        print(f"Effort: {task['effort']}")

        if task['outcomes']:
            print(f"Outcomes: {task['outcomes']}")

        if task['review']:
            print(f"Review: {task['review']}")

        print("\nDates:")
        if task['created_at']:
            created = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
            local_tz = timezone(timedelta(hours=3))  # UTC+3
            local_created = created.astimezone(local_tz)
            print(f" Created at: {local_created.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if task['updated_at']:
            updated = datetime.fromisoformat(task['updated_at'].replace('Z', '+00:00'))
            local_updated = updated.astimezone(local_tz)
            print(f" Last updated: {local_updated.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
        if task['done_at']:
            done = datetime.fromisoformat(task['done_at'].replace('Z', '+00:00'))
            local_done = done.astimezone(local_tz)
            print(f" Done at: {local_done.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
        print("\n" + "=" * 50)

def list_cmd(args):
    list_tasks(args.database_id)

def main():
    parser = argparse.ArgumentParser(description='Manage Notion tasks from command line')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    parser_list = subparsers.add_parser('list', help='List all tasks')
    parser_list.add_argument(
        '--database-id',
        type=str,
        default=os.getenv('NOTION_DATABASE_ID', '26692e6818f880179ee4d9119304e1ac'),
        help='Notion database ID (default: from NOTION_DATABASE_ID env var or hardcoded fallback)'
    )
    parser_list.set_defaults(func=list_cmd)

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    load_dotenv()
    main()
