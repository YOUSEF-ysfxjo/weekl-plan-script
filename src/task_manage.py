import json
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, Any
import markdown as md

# ==============================
# Constants
# ==============================
TIMEZONE = ZoneInfo("Asia/Riyadh")
ALLOWED_STATUS = {"Not St-arted", "In Progress", "Done", "Blocked", "Backlog"}
ALLOWED_PRIORITY = {"Low", "Medium", "High"}
ALLOWED_UPDATE_FIELDS = {"task", "status", "priority", "effort", "outcomes", "review"}

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
# Utility Functions
# ==============================
def get_current_time() -> str:
    return datetime.now(TIMEZONE).isoformat()

def load_tasks() -> Dict[str, Any]:
    try:
        with open("sample.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"tasks": data, "last_updated": get_current_time()}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tasks": [], "last_updated": get_current_time()}

def save_tasks(tasks: Dict[str, Any]) -> None:
    tasks["last_updated"] = get_current_time()
    with open("sample.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)

# ==============================
# Task Management
# ==============================
def add_task(task: str, priority: str = "Low", effort: int = 0, outcomes: str = "",
             review: str = "", status: str = "Not Started") -> str:
    if task == "":
        raise ValueError("Task cannot be empty")
    if priority not in ALLOWED_PRIORITY:
        raise ValueError("Invalid priority")
    if status not in ALLOWED_STATUS:
        raise ValueError("Invalid status")
    if not isinstance(effort, int) or effort < 0:
        raise ValueError("Invalid effort")

    if status == "Done" and (not outcomes or not review):
        raise ValueError("Outcomes and review are required for done tasks")

    tasks = load_tasks()
    task_id = str(uuid.uuid4())
    new_task = {
        "id": task_id,
        "task": task,
        "status": status,
        "priority": priority,
        "effort": effort,
        "outcomes": outcomes,
        "review": review,
        "created_at": get_current_time(),
        "updated_at": get_current_time(),
        "done_at": None
    }
    tasks["tasks"].append(new_task)
    save_tasks(tasks)
    return task_id

def update_task(task_id: str, updates: Dict[str, Any]) -> bool:
    if not task_id or not isinstance(task_id, str):
        raise ValueError("Task id cannot be empty")
    if not isinstance(updates, dict):
        raise ValueError("Updates must be a dictionary")

    for field in updates:
        if field not in ALLOWED_UPDATE_FIELDS:
            raise ValueError(f"Invalid field: {field}")

    if "status" in updates and updates["status"] not in ALLOWED_STATUS:
        raise ValueError("Invalid status")
    if "priority" in updates and updates["priority"] not in ALLOWED_PRIORITY:
        raise ValueError("Invalid priority")

    tasks = load_tasks()
    task_updated = False
    for task in tasks["tasks"]:
        if task["id"] == task_id:
            if "status" in updates:
                task["status"] = updates["status"]
                if updates["status"] == "Done" and not task.get("done_at"):
                    if not task.get("outcomes") or not task.get("review"):
                        raise ValueError("Outcomes and review are required for done tasks")
                    task["done_at"] = get_current_time()
            for field in ["task", "priority", "effort", "outcomes", "review"]:
                if field in updates:
                    task[field] = updates[field]
            task["updated_at"] = get_current_time()
            task_updated = True
            break
    if task_updated:
        save_tasks(tasks)
    return task_updated

def list_tasks() -> None:
    tasks = load_tasks()
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
        print(f"   Created at: {task['created_at']}")
        print(f"   Updated at: {task['updated_at']}")
        if task['done_at']:
            print(f"   Done at: {task['done_at']}")
    print("\n" + "=" * 50)

# ==============================
# Weekly Analysis
# ==============================
def get_weekly_tasks() -> list:
    data = load_tasks()
    weekly_tasks = []
    for task in data.get('tasks', []):
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
    blocked_tasks.sort(key=lambda x: (PRIORITY_MAP.get(x.get('priority', 'Low'), 0), x.get('effort', 0)), reverse=True)
    return blocked_tasks[:3]

def get_next_week_goals(weekly_tasks: list):
    PRIORITY_MAP = {"High": 3, "Medium": 2, "Low": 1}
    goals = [t for t in weekly_tasks if t.get('status') in ['Not Started', 'In Progress']]
    goals.sort(key=lambda x: (PRIORITY_MAP.get(x.get('priority', 'Low'), 0), x.get('effort', 0)), reverse=True)
    return goals[:3]

# ==============================
# Reporting
# ==============================
def generate_weekly_report():
    weekly_tasks = get_weekly_tasks()
    total_tasks, done_count, done_percent, effort_sum, done_effort, effort_percent = calculate_completion(weekly_tasks)

    blocked_tasks = get_top_blockers(weekly_tasks)
    formatted_blockers = "\n".join(
        [f"- {t['task']} (Priority: {t['priority']}, Effort: {t['effort']})" for t in blocked_tasks]
    ) if blocked_tasks else "No blockers this week!"

    next_week_goals = get_next_week_goals(weekly_tasks)
    formatted_goals = "\n".join(
        [f"- {t['task']} (Priority: {t['priority']}, Effort: {t['effort']})" for t in next_week_goals]
    ) if next_week_goals else "No goals this week!"

    markdown_content = f"""# Weekly Report (Week {week_number})

**Date Range:** {week_range}

## Completion
- Count-based: Completed: {done_count} / {total_tasks} ({done_percent:.1f}%)
- Effort-based: Completed Effort: {done_effort} / {effort_sum} ({effort_percent:.1f}%)

## Top 3 Blockers
{formatted_blockers}

## Next Week Goals
{formatted_goals}
"""
    with open('reports/weekly.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    md.markdownFromFile(
        input='reports/weekly.md',
        output='reports/weekly.html'
    )
    print(f"Weekly report generated for Week {week_number} ({week_range})")

# ==============================
# Example Usage
# ==============================
if __name__ == "__main__":
    task_id = add_task("Learn Python")
    update_task(task_id, {"status": "In Progress", "effort": 5})
    list_tasks()
    generate_weekly_report()
