# ZephyrTask

A simple, lightweight Python package for managing tasks with support for prioritization, reminders, and rewards. ZephyrTask provides a clean API for organizing your tasks, reminding you of upcoming deadlines, and rewarding your accomplishments.

## Features

- **Task Management**: Add, update, and remove tasks with customizable time and value parameters
- **Task Listing**: List tasks with various sorting options (upcoming, by priority, etc.)
- **Task Completion**: Mark tasks as completed and track your progress
- **Reminder System**: Get email reminders for upcoming tasks to stay on track
- **Reward System**: Receive motivational rewards when completing tasks of sufficient value

## Installation

### From PyPI (Recommended)

```bash
pip install ZephyrTask
```

### From Source

```bash
# Clone the repository
git clone https://github.com/software-students-spring2025/3-python-package-super-package.git
cd ZephyrTask

# Install in development mode
pip install -e .
```

## Usage

### Core Task Management

```python
import datetime
from ZephyrTask.tasks import add_task, update_task, remove_task

# Add a task with a string time (ISO format)
add_task("2023-06-15T09:00:00", "Morning meeting", 5)

# Add a task with a datetime object
tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
add_task(tomorrow, "Lunch with team", 3)

# Update a task's value
update_task("2023-06-15T09:00:00", "Morning meeting", 10)

# Remove a task
remove_task("2023-06-15T09:00:00", "Morning meeting")
```

### Task Listing (To be implemented by Lan)

```python
from ZephyrTask.list import list_tasks, mark_completed

# List all tasks sorted by time
tasks = list_tasks(sort_by="time")

# List tasks before a specific date
upcoming_tasks = list_tasks(before="2023-07-01T00:00:00")

# Mark a task as completed
mark_completed("2023-06-15T09:00:00", "Morning meeting")
```

### Reminder System (To be implemented by Yuquan)

```python
from ZephyrTask.reminder import reminder_mail

# Configure email reminders
reminder_mail("your_email@example.com", days_ahead=1)
```

### Reward System (To be implemented by Yilei)

```python
from ZephyrTask.reward import reward

# Check rewards when reaching a value threshold
motivational_message = reward(20)
print(motivational_message)  # Prints a joke or congratulatory message
```

## For Contributors

### Development Setup

```bash
# Clone the repository
git clone https://github.com/software-students-spring2025/3-python-package-super-package.git
cd ZephyrTask

# Create and activate a virtual environment
pipenv --python 3.9
pipenv shell

# Install package in development mode
pipenv install -e .

# Install development dependencies
pipenv install pytest build twine

# Run tests
pytest
```

### Development Workflow

1. Create a feature branch for your work

2. Implement your changes and add tests

3. Make sure tests pass
   ```bash
   python -m pytest
   ```

4. Create a pull request to the main branch

## Project Structure

```
ZephyrTask/                         # Root project directory
├── ZephyrTask/                     # Main package source code
│   ├── __init__.py                # Package initialization and exports
│   ├── tasks.py                   # Core task management; Task listing and completion tracking; Email reminder system; Motivational reward system
│   ├── utils/                     # Utility modules
│   │   ├── __init__.py            # Package initialization
│   │   ├── date_utils.py          # Date/time handling utilities
│   │   ├── storage.py             # Data storage abstractions
│   │   └── validators.py          # Input validation functions
│   └── config.py                  # Configuration management
│
├── tests/                         # Test directory
│   ├── __init__.py                # Test package initialization
│   ├── conftest.py                # Pytest fixtures and configuration
│   ├── test_tasks.py              # Tests for tasks module
│   ├── test_list.py               # Tests for list module
│   ├── test_reminder.py           # Tests for reminder module
│   ├── test_reward.py             # Tests for reward module
│   └── utils/                     # Tests for utility modules
│       ├── test_date_utils.py     # Tests for date utilities
│       ├── test_storage.py        # Tests for storage utilities
│       └── test_validators.py     # Tests for validation functions
│
├── examples/                      # Example scripts
│   ├── basic_usage.py             # Basic package usage examples
│   ├── advanced_usage.py          # Advanced features demonstration
│   ├── integration_example.py     # Example integrating all features
│   └── custom_configuration.py    # Customizing package configuration
│
├── docs/                          # Documentation
│   ├── conf.py                    # Sphinx configuration
│   ├── index.rst                  # Documentation home page
│   ├── installation.rst           # Installation guide
│   ├── usage.rst                  # Usage documentation
│   ├── api/                       # API documentation
│   │   ├── tasks.rst              # Tasks API docs
│   │   ├── list.rst               # List API docs
│   │   ├── reminder.rst           # Reminder API docs
│   │   └── reward.rst             # Reward API docs
│   └── _build/                    # Built documentation (not in version control)
│
├── .github/                       # GitHub specific files
│   └── workflows/                 # GitHub Actions workflows
│       ├── python-package.yml     # CI workflow for testing and building
│       └── publish.yml            # Workflow for publishing to PyPI
│
├── .venv/                         # Virtual environment (not in version control)
├── ZephyrTask.egg-info/            # Package metadata (not in version control)
├── .pytest_cache/                 # Pytest cache (not in version control)
│
├── pyproject.toml                 # Project configuration (PEP 517/518)
├── Pipfile                        # Pipenv dependency management
├── Pipfile.lock                   # Locked dependencies (ensure reproducibility)
├── README.md                      # Project documentation
├── LICENSE                        # License information
└── .gitignore                     # Git ignore patterns
```

### Key Modules

- **tasks.py**: 
- Core module for adding, updating, and removing tasks. Tasks are stored as JSON with timestamps, descriptions, values, and completion status.

- Module for listing tasks with various sorting and filtering options, and for marking tasks as completed.
  
- Module for setting up and sending email reminders for upcoming tasks.
  
- Module for providing motivational rewards when users complete tasks of sufficient value.

## Data Storage

By default, tasks are stored in a JSON file at `~/.ZephyrTask_data.json`. Each task has the following structure:

```json
{
  "time": "2023-06-15T09:00:00",
  "event": "Morning meeting",
  "value": 5,
  "completed": false
}
```

You can specify a custom file path when using the API functions.

## Contributors

- [Xingjian](https://github.com/ScottZXJ123) - Core Task Management
- [Lan](https://github.com/ziiiimu) - Task Listing and Completion
- [Yuquan](https://github.com/N-A-E-S) - Email Reminders
- [Yilei](https://github.com/ShadderD) - Reward System

## License

This project is licensed under the MIT License - see the LICENSE file for details.
