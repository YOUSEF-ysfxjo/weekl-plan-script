# Weekly Tasks Script

A Python script to manage and generate weekly reports from Notion task databases.

## Features

- Fetch tasks from a Notion database
- Generate weekly reports in Markdown and HTML formats
- Track task completion and effort metrics
- Identify blockers and set goals for the next week

## Prerequisites

- Python 3.8 or higher
- A Notion account with API access
- A Notion database with the required properties (Task, Status, Priority, Effort, etc.)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/weekly-tasks-script.git
   cd weekly-tasks-script
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On macOS/Linux
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file in the project root with your Notion API token and database ID:
   ```
   NOTION_TOKEN=your_notion_api_token_here
   NOTION_DATABASE_ID=your_database_id_here
   ```

## Usage

### Generate a Weekly Report

```bash
python report.py generate
```

This will create two files in the `reports` directory:
- `weekly.md`: Markdown version of the report
- `weekly.html`: Styled HTML version of the report

### Command Line Options

- `--database-id`: Specify a custom Notion database ID (default: from NOTION_DATABASE_ID env var)

Example:
```bash
python report.py generate --database-id your_database_id_here
```

## Project Structure

- `src/`: Source code for the Notion task manager
  - `data/`: Data handling and Notion API interactions
    - `notion_task_manager.py`: Main Notion API client and task management
- `reports/`: Generated report files (created automatically)
- `report.py`: Main script for generating reports
- `setup.py`: Package configuration

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
