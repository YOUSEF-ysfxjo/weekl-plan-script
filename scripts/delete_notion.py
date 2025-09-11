import os
import sys
import argparse
import requests
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import Notion API configuration
from src.data.notion_task_manager import NOTION_API_URL, NOTION_TOKEN, NOTION_VERSION

def delete_task_notion(task_id: str) -> None:
    """Delete a task from Notion by its ID."""
    url = f"{NOTION_API_URL}/pages/{task_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }
    try:
        response = requests.patch(url, headers=headers, json={"archived": True})
        response.raise_for_status()
        print(f"✅ Successfully deleted task {task_id}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error deleting task: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")

def delete_cmd(args):
    delete_task_notion(args.task_id)

def main():
    parser = argparse.ArgumentParser(description='Delete Notion tasks from command line')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a task')
    parser_delete.add_argument(
        "task_id",
        type=str,
        help='ID of the task to delete'
    )
    parser_delete.set_defaults(func=delete_cmd)

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    load_dotenv()
    main()