import os
import sys
import requests
import markdown as md
import argparse
import json
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================
# Configuration
# ==============================
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

# ==============================
# Constants
# ==============================
NOTION_API_URL = "https://api.notion.com/v1"
DATABASE_ID = NOTION_DATABASE_ID
NOTION_VERSION = "2022-06-28"
TIMEZONE = ZoneInfo("Asia/Riyadh")
ALLOWED_STATUS = {"Not Started", "In Progress", "Done", "Blocked", "Backlog", "In Review"}
ALLOWED_PRIORITY = {"Low", "Medium", "High"}

# Date calculations
START_DATE = datetime(2025, 9, 1).date()
today = datetime.now(TIMEZONE).date()
now = datetime.now(TIMEZONE)
days_since_sunday = now.isoweekday() % 7
midnight_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
week_start = midnight_today - timedelta(days=days_since_sunday)
end_of_week = week_start + timedelta(days=6)
end_of_week = end_of_week.replace(hour=23, minute=59, second=59)
week_number = ((today - START_DATE).days // 7) + 1
date_format = "%Y-%m-%d"
week_range = f"{week_start.strftime(date_format)} to {end_of_week.strftime(date_format)}"

# ==============================
# Notion Functions
# ==============================
def create_page(data: dict):
    url = f"{NOTION_API_URL}/pages"
    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}", 
        "Content-Type": "application/json", 
        "Notion-Version": NOTION_VERSION
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Successfully created page in Notion")
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise  # Re-raise the exception to see the full traceback
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        raise  # Re-raise the exception to see the full traceback

def get_tasks_notion(database_id: str) -> Dict[str, Any]:
    url = f"{NOTION_API_URL}/databases/{database_id}/query"
    
    # Print debug info
    print(f"\n🔍 Fetching tasks from Notion API...")
    print(f"URL: {url}")
    
    try:
        res = requests.post(
            url, 
            headers={
                "Authorization": f"Bearer {NOTION_TOKEN}", 
                "Content-Type": "application/json", 
                "Notion-Version": NOTION_VERSION,
                "Cache-Control": "no-cache"  # Try to prevent caching
            }
        )
        res.raise_for_status()
        
        print(f"✅ Successfully fetched {len(res.json().get('results', []))} tasks")
        
        results = res.json().get("results", [])
        tasks = []
        for row in results:
            props = row["properties"]
            task = {
                "id": row["id"],
                "task": props["Task"]["title"][0]["plain_text"] if props["Task"]["title"] else "",
                "status": props["Status"]["select"]["name"] if props["Status"]["select"] else "",
                "priority": props["Priority"]["select"]["name"] if props["Priority"]["select"] else "",
                "effort": props["Effort"]["number"] if props["Effort"]["number"] is not None else 0,
                "outcomes": props["Outcomes"]["rich_text"][0]["plain_text"] if props["Outcomes"]["rich_text"] else "",
                "review": props["Review"]["rich_text"][0]["plain_text"] if props["Review"]["rich_text"] else "",
                "created_at": row.get("created_time"),
                "updated_at": row.get("last_edited_time"),
                "done_at": props["Done_at"]["date"]["start"] if props["Done_at"]["date"] else None,
            }
            tasks.append(task)
        return {"tasks": tasks, "last_updated": datetime.now(TIMEZONE).isoformat()}
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        raise
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        raise

def get_weekly_tasks(database_id: str, week_start: datetime, end_of_week: datetime) -> list:
    data = get_tasks_notion(database_id)
    weekly_tasks = []
    for task in data.get("tasks", []):
        for field in ["created_at", "updated_at", "done_at"]:
            if task.get(field):
                try:
                    field_dt = datetime.fromisoformat(task[field])
                    if week_start <= field_dt <= end_of_week:
                        weekly_tasks.append(task)
                        break
                except Exception:
                    continue
    return weekly_tasks

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

def delete_task_notion(task_id: str) -> None:
    """
    Archive a task in Notion (soft delete).
    In Notion, pages are archived rather than permanently deleted.
    """
    url = f"{NOTION_API_URL}/pages/{task_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }
    
    # Instead of DELETE, we send a PATCH to set archived to true
    data = {
        "archived": True
    }
    
    try:
        res = requests.patch(url, headers=headers, json=data)
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise Exception(f"Task with ID {task_id} not found or already deleted")
        raise Exception(f"Error archiving task: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def update_task_notion(task_id: str, data: dict):
    # نضيف تحديث التاريخ الحالي للـ Updated_at
    data.setdefault("properties", {})
    data["properties"]["Updated_at"] = {
        "date": {"start": datetime.now().astimezone(timezone.utc).isoformat()}
    }

    url = f"{NOTION_API_URL}/pages/{task_id}"
    res = requests.patch(
        url,
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
        json=data,
    )
    res.raise_for_status()


def list_tasks(database_id: str) -> None:
    tasks = get_tasks_notion(database_id)
    if not tasks["tasks"]:
        print("No tasks found!")
        return

    for task in tasks["tasks"]:
        print("\n" + "="*50)
        print(f"Task: {task['task']}")
        print("-"*30)
        print(f"ID: {task['id']}")
        print(f"Status: {task['status']}")
        print(f"Priority: {task['priority']}")
        if task['effort']:
            print(f"Effort: {task['effort']}")
        if task['outcomes']:
            print(f"Outcomes: {task['outcomes']}")
        if task['review']:
            print(f"Review: {task['review']}")
        
        print("\nDates:")
        if task['created_at']:
            # Parse and format the timestamp in local timezone
            from datetime import datetime, timezone, timedelta
            created = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
            local_tz = timezone(timedelta(hours=3))  # UTC+3
            local_created = created.astimezone(local_tz)
            print(f" Created at: {local_created.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if task['updated_at']:
            # Parse and format the timestamp in local timezone
            updated = datetime.fromisoformat(task['updated_at'].replace('Z', '+00:00'))
            local_updated = updated.astimezone(local_tz)
            print(f" Last updated: {local_updated.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if task['done_at']:
            done = datetime.fromisoformat(task['done_at'].replace('Z', '+00:00'))
            local_done = done.astimezone(local_tz)
            print(f" Done at: {local_done.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        print("\n" + "="*50)

def calculate_completion(weekly_tasks: list) -> tuple:
    total_tasks = len(weekly_tasks)
    done_count = sum(1 for t in weekly_tasks if t.get('done_at'))
    effort_sum = sum(f.get('effort', 0) for f in weekly_tasks)
    sum_done_effort = sum(f.get('effort', 0) for f in weekly_tasks if f.get('done_at'))
    done_count_percentage = (done_count / total_tasks * 100) if total_tasks > 0 else 0
    effort_percentage = (sum_done_effort / effort_sum * 100) if effort_sum > 0 else 0
    return (total_tasks, done_count, done_count_percentage,
            effort_sum, sum_done_effort, effort_percentage)

def get_top_blockers(weekly_tasks: list):
    PRIORITY_MAP = {"High": 3, "Medium": 2, "Low": 1}
    blocked_tasks = [t for t in weekly_tasks if t.get('status') == 'Blocked']
    blocked_tasks.sort(key=lambda x: (PRIORITY_MAP.get(x.get('priority', 'Low'), 0),
                                      x.get('effort', 0)), reverse=True)
    return blocked_tasks[:3]

def get_next_week_goals(weekly_tasks: list):
    PRIORITY_MAP = {"High": 3, "Medium": 2, "Low": 1}
    goals = [t for t in weekly_tasks if t.get('status') in ['Not Started', 'In Progress']]
    goals.sort(key=lambda x: (PRIORITY_MAP.get(x.get('priority', 'Low'), 0),
                              x.get('effort', 0)), reverse=True)
    return goals[:3]

def generate_weekly_report(database_id: str):
    """Generate a weekly report from Notion tasks."""
    try:
        # Calculate date range for the week
        now = datetime.now(TIMEZONE)
        days_since_sunday = now.isoweekday() % 7
        midnight_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = midnight_today - timedelta(days=days_since_sunday)
        end_of_week = week_start + timedelta(days=6)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59)
        
        # Get weekly tasks with the calculated date range
        weekly_tasks = get_weekly_tasks(database_id, week_start, end_of_week)
        
        total_tasks, done_count, done_percent, effort_sum, done_effort, effort_percent = calculate_completion(weekly_tasks)
        
        # Get blocked tasks
        blocked_tasks = get_top_blockers(weekly_tasks)
        formatted_blockers = "\n".join(
            [f"- {t['task']} (Priority: {t['priority']}, Effort: {t['effort']})" for t in blocked_tasks]
        ) if blocked_tasks else "No blockers this week!"
        
        # Get next week's goals
        next_week_goals = get_next_week_goals(weekly_tasks)
        formatted_goals = "\n".join(
            [f"- {t['task']} (Priority: {t['priority']}, Effort: {t['effort']})" for t in next_week_goals]
        ) if next_week_goals else "No goals for next week!"

        # Calculate week number and range for the report
        START_DATE = datetime(2025, 9, 1).date()
        today = datetime.now(TIMEZONE).date()
        week_num = ((today - START_DATE).days // 7) + 1
        date_format = "%Y-%m-%d"
        week_rng = f"{week_start.strftime(date_format)} to {end_of_week.strftime(date_format)}"

        # Generate markdown content
        markdown_content = f"""# Weekly Report (Week {week_num})

**Date Range:** {week_rng}

## Completion
- Count-based: Completed: {done_count} / {total_tasks} ({done_percent:.1f}%)
- Effort-based: Completed Effort: {done_effort} / {effort_sum} ({effort_percent:.1f}%)

## Top 3 Blockers
{formatted_blockers}

## Next Week Goals
{formatted_goals}
"""
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Write markdown file
        md_path = os.path.join("reports", "weekly.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        # Convert to HTML with custom styling
        html_path = os.path.join("reports", "weekly.html")
        with open(md_path, "r", encoding="utf-8") as f:
            html_content = f"""<html>
            <head>
                <title>Weekly Report - Week {week_num}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    .completed {{ color: #27ae60; }}
                    .blockers {{ background-color: #f8d7da; padding: 15px; border-radius: 5px; }}
                    .goals {{ background-color: #d4edda; padding: 15px; border-radius: 5px; }}
                    ul, ol {{ margin: 10px 0; padding-left: 20px; }}
                    li {{ margin: 5px 0; }}
                </style>
            </head>
            <body>
                {markdown_content}
            </body>
            </html>"""
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ Weekly report generated for Week {} ({})".format(week_num, week_rng))
        print("📄 Markdown: {}".format(os.path.abspath(md_path)))
        print("🌐 HTML: {}".format(os.path.abspath(html_path)))
        
    except Exception as e:
        print("❌ Error generating report: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        sys.exit(1)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description='Manage Notion tasks from command line')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('task', help='Task title/description')
    add_parser.add_argument('--priority', choices=ALLOWED_PRIORITY, default='Medium',
                          help='Task priority (default: Medium)')
    add_parser.add_argument('--effort', type=int, default=1, choices=range(1, 6),
                          help='Effort level 1-5 (default: 1)')
    add_parser.add_argument('--status', choices=ALLOWED_STATUS, default='Not Started',
                          help='Task status (default: Not Started)')
    add_parser.add_argument('--outcomes', default='', help='Optional outcomes or notes')
    add_parser.add_argument('--review', default='', help='Optional review notes')
    add_parser.set_defaults(func=handle_add)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument('--database-id', default=NOTION_DATABASE_ID,
                           help=f'Notion database ID (default: {NOTION_DATABASE_ID})')
    list_parser.set_defaults(func=handle_list)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('task_id', help='ID of the task to update')
    update_parser.add_argument('--status', choices=ALLOWED_STATUS, help='New status')
    update_parser.add_argument('--priority', choices=ALLOWED_PRIORITY, help='New priority')
    update_parser.add_argument('--effort', type=int, help='New effort value')
    update_parser.add_argument('--outcomes', help='New outcomes')
    update_parser.add_argument('--review', help='New review')
    update_parser.set_defaults(func=handle_update)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('task_id', help='ID of the task to delete')
    delete_parser.set_defaults(func=handle_delete)
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate weekly report')
    report_parser.add_argument('--database-id', default=NOTION_DATABASE_ID,
                             help=f'Notion database ID (default: {NOTION_DATABASE_ID})')
    report_parser.set_defaults(func=handle_report)
    
    return parser

def handle_add(args) -> None:
    """Handle the add command."""
    try:
        result = add_task_notion(
            task=args.task,
            priority=args.priority,
            effort=args.effort,
            status=args.status,
            outcomes=args.outcomes,
            review=args.review
        )
        print(f"✅ Task added successfully! ID: {result.get('id')}")
    except Exception as e:
        print(f"❌ Error adding task: {str(e)}")
        sys.exit(1)

def handle_list(args) -> None:
    """Handle the list command."""
    try:
        list_tasks(args.database_id)
    except Exception as e:
        print(f"❌ Error listing tasks: {str(e)}")
        sys.exit(1)

def handle_update(args) -> None:
    """Handle the update command."""
    try:
        # Get current task data
        task_data = get_tasks_notion(NOTION_DATABASE_ID)
        current_task = next((t for t in task_data['tasks'] if t['id'] == args.task_id), None)
        
        if not current_task:
            print(f"❌ Error: Task {args.task_id} not found")
            sys.exit(1)
            
        # Check if updating to Done without required fields
        if args.status == 'Done' or (not args.status and current_task['status'] == 'Done'):
            if (not args.outcomes and not current_task['outcomes']) or \
               (not args.review and not current_task['review']):
                print("❌ Error: Cannot mark task as Done without both outcomes and review")
                print("Please provide both --outcomes and --review when marking as Done")
                sys.exit(1)
                
        data = {}
        if args.status:
            data['Status'] = {'select': {'name': args.status}}
        if args.priority:
            data['Priority'] = {'select': {'name': args.priority}}
        if args.effort is not None:
            data['Effort'] = {'number': args.effort}
        if args.outcomes is not None:
            data['Outcomes'] = {'rich_text': [{'text': {'content': args.outcomes}}]}
        if args.review is not None:
            data['Review'] = {'rich_text': [{'text': {'content': args.review}}]}
            
        update_task_notion(args.task_id, {"properties": data})
        print(f"✅ Task {args.task_id} updated successfully!")
    except Exception as e:
        print(f"❌ Error updating task: {str(e)}")
        sys.exit(1)

def handle_delete(args) -> None:
    """Handle the delete command."""
    try:
        delete_task_notion(args.task_id)
        print(f"✅ Task {args.task_id} deleted successfully!")
    except Exception as e:
        print(f"❌ Error deleting task: {str(e)}")
        sys.exit(1)

def handle_report(args) -> None:
    """Handle the report command."""
    try:
        generate_weekly_report(args.database_id)
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        sys.exit(1)

def main() -> None:
    """Main entry point for the CLI."""
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("Error: NOTION_TOKEN and NOTION_DATABASE_ID must be set in environment")
        sys.exit(1)
        
    parser = setup_argparse()
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    load_dotenv()
    main()
