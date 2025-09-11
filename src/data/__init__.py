# This file makes the data directory a Python package

# Import and expose the main functions
from .notion_task_manager import (
    get_weekly_tasks,
    calculate_completion,
    get_top_blockers,
    get_next_week_goals,
    generate_weekly_report,
    get_tasks_notion,
    add_task_notion,
    delete_task_notion,
    list_tasks
)

__all__ = [
    'get_weekly_tasks',
    'calculate_completion',
    'get_top_blockers',
    'get_next_week_goals',
    'generate_weekly_report',
    'get_tasks_notion',
    'add_task_notion',
    'delete_task_notion',
    'list_tasks'
]
