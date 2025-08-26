import json
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional

# Constants
TIMEZONE = ZoneInfo("Asia/Riyadh")
ALLOWED_STATUS = {"Not Started", "In Progress", "Done", "Blocked", "Backlog"}
ALLOWED_PRIORITY = {"Low", "Medium", "High"}
ALLOWED_UPDATE_FIELDS = {"task", "status", "priority", "effort", "outcomes", "review"}

def get_current_time() -> str:
    return datetime.now(TIMEZONE).isoformat()

def load_tasks() -> Dict[str, Any]:
    """
    Load tasks from file
    """
    try:
        with open("sample.json", "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"tasks": data, "last_updated": get_current_time()}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tasks": [], "last_updated": get_current_time()}

def save_tasks(tasks: Dict[str, Any]) -> None:
    """
    Save tasks to file
    """
    tasks["last_updated"] = get_current_time()
    with open("sample.json", "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(task: str, priority: str = "Low", effort: int = 0, outcomes: str = "", 
             review: str = "", status: str = "Not Started") -> str:
    """
    Add a new task
    
    Args:
        task: The task description
        priority: The task priority (Low/Medium/High)
        effort: The effort required (0-10)
        outcomes: Task outcomes when completed
        review: Review of the task
        status: Task status (Not Started/In Progress/Done/Blocked/Backlog)
    
    Returns:
        str: The task id
    """
    if task == "":
        raise ValueError("Task cannot be empty")
    
    if priority not in ALLOWED_PRIORITY:
        raise ValueError("Invalid priority")
    
    if status not in ALLOWED_STATUS:
        raise ValueError("Invalid status")
        
    if not isinstance(effort, int) or effort < 0:
        raise ValueError("Invalid effort")
        
    if outcomes and not isinstance(outcomes, str):
        raise ValueError("Invalid outcomes")
        
    if review and not isinstance(review, str):
        raise ValueError("Invalid review")
        
    if status == "Done":
        if not outcomes or not review:
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
    
    try:
        tasks["tasks"].append(new_task)
        save_tasks(tasks)
        return task_id
    except Exception as e:
        print(f"Error adding task: {e}")
        raise

def update_task(task_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update a task
    
    Args:
        task_id: The task id to update
        updates: Dictionary of fields to update
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    if not task_id or not isinstance(task_id, str):
        raise ValueError("Task id cannot be empty")
    
    if not isinstance(updates, dict):
        raise ValueError("Updates must be a dictionary")
    
    # Check for invalid fields
    for field in updates:
        if field not in ALLOWED_UPDATE_FIELDS:
            raise ValueError(f"Invalid field: {field}")
    
    # Validate field values
    if "status" in updates:
        if updates["status"] not in ALLOWED_STATUS:
            raise ValueError("Invalid status")
            
    if "priority" in updates and updates["priority"] not in ALLOWED_PRIORITY:
        raise ValueError("Invalid priority")
        
    if "effort" in updates and (not isinstance(updates["effort"], int) or updates["effort"] < 0):
        raise ValueError("Invalid effort")
        
    if "outcomes" in updates and not isinstance(updates["outcomes"], str):
        raise ValueError("Outcomes must be a string")
        
    if "review" in updates and not isinstance(updates["review"], str):
        raise ValueError("Review must be a string")
    
    # Remove done_at from updates if present (should be set by the system only)
    if 'done_at' in updates:
        del updates['done_at']
        
    # Create a temporary task with merged updates to validate Done status
    temp_task = None
    if 'status' in updates and updates['status'] == 'Done':
        tasks = load_tasks()
        for task in tasks["tasks"]:
            if task["id"] == task_id:
                # Create a copy of current task and apply updates
                temp_task = task.copy()
                for key, value in updates.items():
                    if key in ALLOWED_UPDATE_FIELDS:
                        temp_task[key] = value
                break
                
        # If we couldn't find the task, we'll let the normal flow handle the error
        if temp_task:
            if not temp_task.get('outcomes') or not temp_task.get('review'):
                raise ValueError("Outcomes and review are required for done tasks")
    
    tasks = load_tasks()
    task_updated = False
    
    for task in tasks["tasks"]:
        if task["id"] == task_id:
            # Update status and set done_at if marking as Done
            if "status" in updates:
                task["status"] = updates["status"]
                if updates["status"] == "Done" and not task.get("done_at"):
                    task["done_at"] = get_current_time()
            
            # Update other fields (excluding done_at)
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
    """
    List all tasks
    """
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

if __name__ == "__main__":
    # Example usage
    task_id = add_task("Learn Python")
    update_task(task_id, {
        "status": "In Progress",
        "effort": 5
    })
    list_tasks()
