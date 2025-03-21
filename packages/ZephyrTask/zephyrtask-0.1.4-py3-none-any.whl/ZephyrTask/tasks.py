"""
Tasks module for the Pytask package.

This module provides core functionality for managing tasks, including
adding, updating, and removing tasks.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import smtplib
import ssl
import pyjokes
from email.message import EmailMessage


# Define the default location for the tasks data file
DEFAULT_TASKS_FILE = os.path.expanduser("~/.ZephyrTask_data.json")


def _get_tasks(tasks_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Internal function to get tasks from the data file.
    
    Args:
        tasks_file: Optional path to the tasks file. Defaults to DEFAULT_TASKS_FILE.
        
    Returns:
        List of task dictionaries.
    """
    tasks_file = tasks_file or DEFAULT_TASKS_FILE
    
    # If the file doesn't exist, return an empty list
    if not os.path.exists(tasks_file):
        return []
    
    try:
        with open(tasks_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If there's an error reading the file, return an empty list
        return []


def _save_tasks(tasks: List[Dict[str, Any]], tasks_file: Optional[str] = None) -> None:
    """
    Internal function to save tasks to the data file.
    
    Args:
        tasks: List of task dictionaries to save.
        tasks_file: Optional path to the tasks file. Defaults to DEFAULT_TASKS_FILE.
    """
    tasks_file = tasks_file or DEFAULT_TASKS_FILE
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(tasks_file)), exist_ok=True)
    
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)


def _validate_task(time: Union[str, datetime.datetime], event: str, value: int) -> Dict[str, Any]:
    """
    Validate and format task data.
    
    Args:
        time: Task time as string (ISO format) or datetime object.
        event: Task description/name.
        value: Task value (integer).
        
    Returns:
        Dictionary with validated task data.
        
    Raises:
        ValueError: If any of the arguments are invalid.
    """
    # Validate time
    if isinstance(time, str):
        try:
            parsed_time = datetime.datetime.fromisoformat(time)
            time_str = time
        except ValueError:
            raise ValueError(f"Invalid time format: {time}. Use ISO format (YYYY-MM-DDThh:mm:ss).")
    elif isinstance(time, datetime.datetime):
        time_str = time.isoformat()
    else:
        raise ValueError(f"Time must be a string in ISO format or a datetime object, got {type(time)}")
    
    # Validate event
    if not isinstance(event, str) or not event.strip():
        raise ValueError("Event must be a non-empty string")
    
    # Validate value
    if not isinstance(value, int):
        raise ValueError(f"Value must be an integer, got {type(value)}")
    
    return {
        "time": time_str,
        "event": event.strip(),
        "value": value,
        "completed": False
    }


def add_task(time: Union[str, datetime.datetime], event: str, value: int, 
             tasks_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a new task.
    
    Args:
        time: Task time as string (ISO format) or datetime object.
        event: Task description/name.
        value: Task value (integer).
        tasks_file: Optional path to the tasks file. Defaults to DEFAULT_TASKS_FILE.
        
    Returns:
        The newly added task as a dictionary.
        
    Raises:
        ValueError: If a task with the same time and event already exists or if 
                    any of the arguments are invalid.
    """
    # Get existing tasks
    tasks = _get_tasks(tasks_file)
    
    # Validate task data
    new_task = _validate_task(time, event, value)
    
    # Check if a task with the same time and event already exists
    for task in tasks:
        if task["time"] == new_task["time"] and task["event"] == new_task["event"]:
            raise ValueError(f"Task with time '{new_task['time']}' and event '{new_task['event']}' already exists")
    
    # Add the new task
    tasks.append(new_task)
    
    # Save tasks
    _save_tasks(tasks, tasks_file)
    
    return new_task


def update_task(time: Union[str, datetime.datetime], event: str, value: int, 
                tasks_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an existing task.
    
    Args:
        time: Task time as string (ISO format) or datetime object.
        event: Task description/name to identify the task.
        value: New task value.
        tasks_file: Optional path to the tasks file. Defaults to DEFAULT_TASKS_FILE.
        
    Returns:
        The updated task as a dictionary.
        
    Raises:
        ValueError: If the task doesn't exist or if any of the arguments are invalid.
    """
    # Validate task data
    validated_task = _validate_task(time, event, value)
    time_str = validated_task["time"]
    event_str = validated_task["event"]
    
    # Get existing tasks
    tasks = _get_tasks(tasks_file)
    
    # Find and update the task
    for i, task in enumerate(tasks):
        if task["time"] == time_str and task["event"] == event_str:
            # Update the value (keeping completion status intact)
            tasks[i]["value"] = value
            
            # Save tasks
            _save_tasks(tasks, tasks_file)
            
            return tasks[i]
    
    # If we get here, the task wasn't found
    raise ValueError(f"No task found with time '{time_str}' and event '{event_str}'")


def remove_task(time: Union[str, datetime.datetime], event: str, 
                tasks_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Remove an existing task.
    
    Args:
        time: Task time as string (ISO format) or datetime object.
        event: Task description/name to identify the task.
        tasks_file: Optional path to the tasks file. Defaults to DEFAULT_TASKS_FILE.
        
    Returns:
        The removed task as a dictionary.
        
    Raises:
        ValueError: If the task doesn't exist or if any of the arguments are invalid.
    """
    # Convert time to string if it's a datetime object
    if isinstance(time, datetime.datetime):
        time_str = time.isoformat()
    else:
        time_str = time
    
    # Get existing tasks
    tasks = _get_tasks(tasks_file)
    
    # Find and remove the task
    for i, task in enumerate(tasks):
        if task["time"] == time_str and task["event"] == event:
            # Remove the task
            removed_task = tasks.pop(i)
            
            # Save tasks
            _save_tasks(tasks, tasks_file)
            
            return removed_task
    
    # If we get here, the task wasn't found
    raise ValueError(f"No task found with time '{time_str}' and event '{event}'") 


def complete(event: str, tasks_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Marks a task as completed by its event name.

    Args:
        event (str): The name/description of the task.
        tasks_file (Optional[str]): Path to the tasks file.

    Returns:
        Dict[str, Any]: The updated task.

    Raises:
        ValueError: If no matching task is found.
    """
    tasks = _get_tasks(tasks_file)
    
    for task in tasks:
        if task["event"] == event:
            task["completed"] = True  # Mark as completed
            _save_tasks(tasks, tasks_file)
            return task  # Return the updated task

    raise ValueError(f"No task found with event '{event}'")


def list_tasks(order_by: str = "time", tasks_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lists tasks sorted by deadline (time) or value.

    Args:
        order_by (str): Sorting order - "time" (default) or "value".
        tasks_file (Optional[str]): Path to the tasks file.

    Returns:
        List[Dict[str, Any]]: Sorted list of tasks.

    Raises:
        ValueError: If an invalid sorting key is provided.
    """
    tasks = _get_tasks(tasks_file)
    
    if order_by == "time":
        tasks.sort(key=lambda task: task["time"])  # Sort by deadline
    elif order_by == "value":
        tasks.sort(key=lambda task: task["value"], reverse=True)  # Sort by highest value first
    else:
        raise ValueError("Invalid sort order. Choose 'time' or 'value'.")

    return tasks



def reminder(
    tasks_file: Optional[str] = None,
    to_email: str = "",
    deadline: int = 24,
    from_email: str = "13601583609@163.com",
    smtp_server: str = "smtp.163.com",
    smtp_port: int = 465,
    login: str = "13601583609@163.com",
    password: str = "APYDOSTDPDUOEEHQ",
    additional_text: str = "",
    rank: str = "time" 
) -> None:
    """
    Send a reminder email for upcoming tasks, sorted by time or value,
    and displayed in an HTML table.

    Args:
        tasks_file:     path to the tasks file. Defaults to DEFAULT_TASKS_FILE.
        to_email:       addressee's email address.
        deadline:       deadline for reminder in hours. default 24.
        from_email:     sender's email address. default set
        smtp_server:    
        smtp_port:     
        login:          
        password:       
        additional_text:
        rank:           How to rank the tasks. "time" for time, "value" for value. default "time".
    """

    print("DEBUG in tasks.py: smtplib.SMTP_SSL =", smtplib.SMTP_SSL)
    tasks_file = tasks_file or DEFAULT_TASKS_FILE
    current_time = datetime.datetime.now()
    tasks = _get_tasks(tasks_file)
    upcoming_tasks = []
    for task in tasks:
        task_time = datetime.datetime.fromisoformat(task["time"])
        if not task.get("completed", False):
            diff_hours = (task_time - current_time).total_seconds() / 3600
            if diff_hours <= deadline:
                upcoming_tasks.append(task)

    if not upcoming_tasks:
        return

    if rank == "value":
        upcoming_tasks.sort(key=lambda t: t["value"])
    else:
        upcoming_tasks.sort(key=lambda t: datetime.datetime.fromisoformat(t["time"]))

    # build the email message
    message = EmailMessage()
    message["Subject"] = "Upcoming Task Reminder"
    message["From"] = from_email
    message["To"] = to_email

    # pure text part of the email as a backup
    message.set_content(
        "You have upcoming tasks.\n"
        f"Deadline window: {deadline} hours.\n"
        f"{additional_text}\n\n"
        "Please view the HTML part for a detailed table."
    )
    # HTML Format
    html_content = f"""
    <html>
    <body>
      <p>You have <b>{len(upcoming_tasks)}</b> upcoming task(s)
         within the next {deadline} hour(s).<br>
         {additional_text}</p>
      <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <tr>
          <th>Time</th>
          <th>Event</th>
          <th>Value</th>
        </tr>
    """

    for task in upcoming_tasks:
        html_content += f"""
        <tr>
          <td>{task['time']}</td>
          <td>{task['event']}</td>
          <td>{task['value']}</td>
        </tr>
        """

    html_content += """
      </table>
    </body>
    </html>
    """

    message.add_alternative(html_content, subtype="html")
    # Send
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(login, password)
        server.send_message(message)
        server.quit()

    print("Reminder email sent successfully.")


def reward(
    threshold_value: int,
    tasks_file: Optional[str] = None,
    to_email: str = "",
    from_email: str = "13601583609@163.com",
    smtp_server: str = "smtp.163.com",
    smtp_port: int = 465,
    login: str = "13601583609@163.com",
    password: str = "APYDOSTDPDUOEEHQ",
    reward_message: str = "Congratulations on reaching your goal!",
    include_completed_tasks: bool = True,
    include_joke: bool = True
) -> bool:
    """
    Check if the total value of completed tasks meets or exceeds a threshold value,
    and send a reward notification email if it does.

    Args:
        threshold_value:       The minimum total value required to trigger the reward.
        tasks_file:            Path to the tasks file. Defaults to DEFAULT_TASKS_FILE.
        to_email:              Addressee's email address.
        from_email:            Sender's email address. Default set.
        smtp_server:           SMTP server for sending email.
        smtp_port:             SMTP port for sending email.
        login:                 Login credential for SMTP server.
        password:              Password for SMTP server.
        reward_message:        Custom message to include in the reward email.
        include_completed_tasks: Whether to include the list of completed tasks in the email.
        include_joke:          Whether to include a programming joke in the email.

    Returns:
        bool: True if the reward email was sent, False otherwise.
    """
    tasks_file = tasks_file or DEFAULT_TASKS_FILE
    tasks = _get_tasks(tasks_file)
    
    # Calculate total value of completed tasks
    completed_tasks = [task for task in tasks if task.get("completed", False) is True]
    total_value = sum(task["value"] for task in completed_tasks)
    
    # If total value doesn't meet threshold, do nothing
    if total_value < threshold_value:
        return False
    
    # Get a joke if requested
    joke = pyjokes.get_joke() if include_joke else ""
    
    # Build the email message
    message = EmailMessage()
    message["Subject"] = f"Goal Achievement Reward: {total_value} points"
    message["From"] = from_email
    message["To"] = to_email
    
    # Plain text part of the email as a backup
    message.set_content(
        f"Congratulations! You have reached {total_value} points, meeting your goal of {threshold_value}.\n"
        f"{reward_message}\n\n"
        f"{joke}\n\n" if include_joke else ""
        "Please view the HTML part for more details."
    )
    
    # HTML Format
    # Initialize the html_content variable first
    html_content = f"""
    <html>
    <body>
    <h2>Congratulations on Your Achievement!</h2>
    <p>You have earned a total of <b>{total_value}</b> points,
        meeting your goal of <b>{threshold_value}</b>.</p>
    <p>{reward_message}</p>
    """

    # Add the joke section as a separate string concatenation
    if include_joke:
        html_content += f"""<p><i>Here's a joke to celebrate: "{joke}"</i></p>"""

    # Add completed tasks if requested
    if include_completed_tasks and completed_tasks:
        html_content += f"""
    <h3>Your Completed Tasks:</h3>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <tr>
        <th>Time</th>
        <th>Event</th>
        <th>Value</th>
        </tr>
        """
    # Rest of your table content
        
        for task in completed_tasks:
            html_content += f"""
            <tr>
              <td>{task['time']}</td>
              <td>{task['event']}</td>
              <td>{task['value']}</td>
            </tr>
            """
            
        html_content += """
          </table>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    message.add_alternative(html_content, subtype="html")
    
    # Send email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(login, password)
            server.send_message(message)
            server.quit()
        
        print("Reward notification email sent successfully.")
        return True
    except Exception as e:
        print(f"Failed to send reward email: {e}")
        return False