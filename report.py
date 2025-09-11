#!/usr/bin/env python3

import os
import sys
import argparse
import markdown as md
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import from the src package
    from src import (
        get_weekly_tasks,
        calculate_completion,
        get_top_blockers,
        get_next_week_goals
    )
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Make sure you have installed the package in development mode with: pip install -e .")
    sys.exit(1)

def generate_weekly_report(database_id: str) -> None:
    """Generate a weekly report from Notion tasks."""
    try:
        # Calculate date range for the week
        TIMEZONE = ZoneInfo("Asia/Riyadh")
        now = datetime.now(TIMEZONE)
        days_since_sunday = now.isoweekday() % 7
        midnight_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = midnight_today - timedelta(days=days_since_sunday)
        end_of_week = week_start + timedelta(days=6)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59)
        
        print(f"📅 Generating report for week: {week_start.date()} to {end_of_week.date()}")
        
        # Get weekly tasks with the calculated date range
        print("🔍 Fetching tasks from Notion...")
        weekly_tasks = get_weekly_tasks(database_id, week_start, end_of_week)
        
        if not weekly_tasks:
            print("ℹ️ No tasks found for this week.")
            return
            
        print(f"✅ Found {len(weekly_tasks)} tasks for this week")
        
        # Calculate completion metrics
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
        html_content = """<html>
        <head>
            <title>Weekly Report - Week {week_num}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .completed {{ color: #27ae60; }}
                .blockers {{ background-color: #f8d7da; padding: 15px; border-radius: 5px; }}
                .goals {{ background-color: #d4edda; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            {markdown_content}
        </body>
        </html>""".format(
            week_num=week_num,
            markdown_content=md.markdown(markdown_content)
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ Weekly report generated for Week {week_num} ({week_rng})")
        print(f"📄 Markdown: {os.path.abspath(md_path)}")
        print(f"🌐 HTML: {os.path.abspath(html_path)}")
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def generate_cmd(args):
    """Handle the generate command."""
    generate_weekly_report(args.database_id)

def main():
    parser = argparse.ArgumentParser(description='Generate weekly reports from Notion tasks')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate report command
    parser_generate = subparsers.add_parser('generate', help='Generate weekly report')
    parser_generate.add_argument(
        '--database-id',
        type=str,
        default=os.getenv('NOTION_DATABASE_ID', '26692e6818f880179ee4d9119304e1ac'),
        help='Notion database ID (default: from NOTION_DATABASE_ID env var or hardcoded fallback)'
    )
    parser_generate.set_defaults(func=generate_cmd)

    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    load_dotenv()
    main()