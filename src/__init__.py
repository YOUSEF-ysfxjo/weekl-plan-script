# This file makes the src directory a Python package

# Import and expose the main functions
from .data.notion_task_manager import (
    get_weekly_tasks,
    calculate_completion,
    get_top_blockers,
    get_next_week_goals,
    generate_weekly_report
)

__all__ = [
    'get_weekly_tasks',
    'calculate_completion',
    'get_top_blockers',
    'get_next_week_goals',
    'generate_weekly_report'
]
