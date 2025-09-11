import os
import sys
import argparse
from dotenv import load_dotenv
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data.notion_task_manager import create_page


def add_task_notion(task: str, priority: str = "Low", effort: int = 0,
                    outcomes: str = "", review: str = "",
                    status: str = "Not Started") -> str:
    created_at = datetime.now().astimezone(timezone.utc).isoformat()
    updated_at = datetime.now().astimezone(timezone.utc).isoformat()
    done_at = datetime.now().astimezone(timezone.utc).isoformat()
    data = {
        "Task": {"title": [{"text": {"content": task}}]},
        "Status": {"select": {"name": status}},
        "Priority": {"select": {"name": priority}},
        "Effort": {"number": effort},
        "Outcomes": {"rich_text": [{"text": {"content": outcomes}}]},
        "Review": {"rich_text": [{"text": {"content": review}}]},
        "Created_at": {"date": {"start": created_at}},
        "Updated_at": {"date": {"start": updated_at}}
    }
    if status == "Done":
        data["Done_at"] = {"date": {"start": done_at}}
    res = create_page(data)
    return res

def add_cmd(args):
    add_task_notion(args.task, args.priority, args.effort, args.outcomes, args.review, args.status)

def main():
    parser = argparse.ArgumentParser(description='Manage Notion tasks from command line')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    parser_add = subparsers.add_parser('add', help='Add a new task')

    parser_add.add_argument(
        "task",
        type=str,
        help='Task title/description'
    )
    parser_add.add_argument(
        "--priority",
        type=str,
        choices=["High", "Medium", "Low"],
        default="Medium",
        help='Task priority (default: Medium)'
    )
    parser_add.add_argument(
        "--effort",
        type=int,
        choices=range(1, 6),
        default=1,
        help='Effort level 1-5 (default: 1)'
    )
    parser_add.add_argument(
        "--status",
        type=str,
        choices=["Not Started", "In Progress", "Done", "Blocked"],
        default="Not Started",
        help='Task status (default: Not Started)'
    )
    parser_add.add_argument(
        "--outcomes",
        type=str,
        default="",
        help='Optional outcomes or notes for the task'
    )
    parser_add.add_argument(
        "--review",
        type=str,
        default="",
        help='Optional review notes for the task'
    )

    parser_add.set_defaults(func=add_cmd)

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    load_dotenv()
    main()
