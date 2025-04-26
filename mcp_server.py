from mcp.server.fastmcp import FastMCP, Context
import requests
import json
import re

# Create an MCP server
mcp = FastMCP("Todo List MCP Server")

# Flask app URL (assuming it's running locally)
FLASK_URL = "http://127.0.0.1:5000"

# Helper functions
def extract_contexts_projects(text):
    """Extract contexts and projects from task text"""
    contexts = re.findall(r'@(\w+)', text)
    projects = re.findall(r'\+(\w+)', text)
    return contexts, projects

def format_task(task_dict):
    """Format a task dictionary into a readable string"""
    priority = f"({task_dict['priority']}) " if task_dict.get('priority') else ""
    created_date = f"[Created: {task_dict['created_date']}] " if task_dict.get('created_date') else ""
    completed = "[COMPLETED] " if task_dict.get('completed') == 1 else ""
    completed_date = f"[Completed: {task_dict['completed_date']}] " if task_dict.get('completed_date') else ""
    
    return f"{completed}{priority}{created_date}{completed_date}{task_dict['text']} (ID: {task_dict['id']})"

# Resources
@mcp.resource("todo://tasks")
def get_all_tasks() -> str:
    """Get all tasks from the todo list"""
    try:
        response = requests.get(f"{FLASK_URL}/")
        if response.status_code != 200:
            return f"Error fetching tasks: HTTP {response.status_code}"
        
        # Parse HTML to extract tasks (simplified approach)
        html = response.text
        
        # This is a simplified approach - in a real implementation, 
        # you might want to use a proper HTML parser like BeautifulSoup
        active_tasks_section = html.split('Active Tasks')[1].split('Completed Tasks')[0]
        active_tasks_items = re.findall(r'<li class="list-group-item.*?>(.*?)</li>', active_tasks_section, re.DOTALL)
        
        completed_tasks_section = html.split('Completed Tasks')[1] if 'Completed Tasks' in html else ""
        completed_tasks_items = re.findall(r'<li class="list-group-item.*?>(.*?)</li>', completed_tasks_section, re.DOTALL)
        
        # Format the output
        result = "# Todo List\n\n## Active Tasks:\n"
        for i, task_html in enumerate(active_tasks_items):
            # Extract task ID
            task_id = re.search(r'complete_task/(\d+)', task_html)
            if task_id:
                task_id = task_id.group(1)
                
            # Extract task text (simplified)
            task_text = re.sub(r'<.*?>', ' ', task_html)
            task_text = re.sub(r'\s+', ' ', task_text).strip()
            
            result += f"{i+1}. {task_text} (ID: {task_id})\n"
        
        result += "\n## Completed Tasks:\n"
        for i, task_html in enumerate(completed_tasks_items):
            # Extract task ID
            task_id = re.search(r'uncomplete_task/(\d+)', task_html)
            if task_id:
                task_id = task_id.group(1)
                
            # Extract task text (simplified)
            task_text = re.sub(r'<.*?>', ' ', task_html)
            task_text = re.sub(r'\s+', ' ', task_text).strip()
            
            result += f"{i+1}. {task_text} (ID: {task_id})\n"
        
        return result
    except Exception as e:
        return f"Error fetching tasks: {str(e)}"

@mcp.resource("todo://task/{task_id}")
def get_task(task_id: str) -> str:
    """Get details for a specific task by ID"""
    try:
        # For a real implementation, you might want to create a new endpoint in the Flask app
        # that returns details for a specific task. For now, we'll get all tasks and filter.
        response = requests.get(f"{FLASK_URL}/")
        if response.status_code != 200:
            return f"Error fetching task: HTTP {response.status_code}"
        
        # Parse HTML to find the specific task (simplified approach)
        html = response.text
        
        # Look for the task in both active and completed sections
        task_pattern = rf'<li class="list-group-item.*?(?:complete_task|uncomplete_task)/{task_id}.*?>(.*?)</li>'
        task_match = re.search(task_pattern, html, re.DOTALL)
        
        if not task_match:
            return f"Task with ID {task_id} not found."
        
        task_html = task_match.group(1)
        
        # Extract task details (simplified)
        task_text = re.sub(r'<.*?>', ' ', task_html)
        task_text = re.sub(r'\s+', ' ', task_text).strip()
        
        # Check if task is completed
        is_completed = 'uncomplete_task' in task_html
        status = "Completed" if is_completed else "Active"
        
        # Extract priority if present
        priority_match = re.search(r'priority-([A-Z])', task_html)
        priority = priority_match.group(1) if priority_match else "None"
        
        # Extract dates if present
        created_date_match = re.search(r'Created: ([\d-]+)', task_html)
        created_date = created_date_match.group(1) if created_date_match else "Unknown"
        
        completed_date = "N/A"
        if is_completed:
            completed_date_match = re.search(r'Completed: ([\d-]+)', task_html)
            completed_date = completed_date_match.group(1) if completed_date_match else "Unknown"
        
        # Extract contexts and projects
        contexts = re.findall(r'class="context">(@\w+)', task_html)
        projects = re.findall(r'class="project">(\+\w+)', task_html)
        
        result = f"# Task {task_id}\n\n"
        result += f"Text: {task_text}\n"
        result += f"Status: {status}\n"
        result += f"Priority: {priority}\n"
        result += f"Created: {created_date}\n"
        
        if is_completed:
            result += f"Completed: {completed_date}\n"
        
        if contexts:
            result += f"Contexts: {', '.join(contexts)}\n"
        
        if projects:
            result += f"Projects: {', '.join(projects)}\n"
        
        return result
    except Exception as e:
        return f"Error fetching task: {str(e)}"

@mcp.resource("todo://contexts")
def get_contexts() -> str:
    """Get all contexts used in tasks"""
    try:
        response = requests.get(f"{FLASK_URL}/")
        if response.status_code != 200:
            return f"Error fetching contexts: HTTP {response.status_code}"
        
        # Parse HTML to extract contexts
        html = response.text
        contexts = re.findall(r'class="context">(@\w+)', html)
        
        # Remove duplicates and sort
        unique_contexts = sorted(set(contexts))
        
        if not unique_contexts:
            return "No contexts found in tasks."
        
        result = "# Available Contexts\n\n"
        for i, context in enumerate(unique_contexts):
            result += f"{i+1}. {context}\n"
        
        return result
    except Exception as e:
        return f"Error fetching contexts: {str(e)}"

@mcp.resource("todo://projects")
def get_projects() -> str:
    """Get all projects used in tasks"""
    try:
        response = requests.get(f"{FLASK_URL}/")
        if response.status_code != 200:
            return f"Error fetching projects: HTTP {response.status_code}"
        
        # Parse HTML to extract projects
        html = response.text
        projects = re.findall(r'class="project">(\+\w+)', html)
        
        # Remove duplicates and sort
        unique_projects = sorted(set(projects))
        
        if not unique_projects:
            return "No projects found in tasks."
        
        result = "# Available Projects\n\n"
        for i, project in enumerate(unique_projects):
            result += f"{i+1}. {project}\n"
        
        return result
    except Exception as e:
        return f"Error fetching projects: {str(e)}"

# Tools
@mcp.tool()
def add_task(text: str) -> str:
    """
    Add a new task to the todo list.
    
    Args:
        text: The task text. Can include priority in format (A) and contexts/projects like @context +project
    """
    try:
        # Send POST request to add task
        response = requests.post(
            f"{FLASK_URL}/add",
            data={"text": text},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return f"Task added successfully: {text}"
        else:
            return f"Error adding task: HTTP {response.status_code}"
    except Exception as e:
        return f"Error adding task: {str(e)}"

@mcp.tool()
def complete_task(task_id: int) -> str:
    """
    Mark a task as complete.
    
    Args:
        task_id: The ID of the task to mark as complete
    """
    try:
        # Send POST request to complete task
        response = requests.post(f"{FLASK_URL}/complete/{task_id}")
        
        if response.status_code == 200:
            return f"Task {task_id} marked as complete"
        else:
            return f"Error completing task: HTTP {response.status_code}"
    except Exception as e:
        return f"Error completing task: {str(e)}"

@mcp.tool()
def uncomplete_task(task_id: int) -> str:
    """
    Mark a completed task as incomplete.
    
    Args:
        task_id: The ID of the task to mark as incomplete
    """
    try:
        # Send POST request to uncomplete task
        response = requests.post(f"{FLASK_URL}/uncomplete/{task_id}")
        
        if response.status_code == 200:
            return f"Task {task_id} marked as incomplete"
        else:
            return f"Error uncompleting task: HTTP {response.status_code}"
    except Exception as e:
        return f"Error uncompleting task: {str(e)}"

@mcp.tool()
def delete_task(task_id: int) -> str:
    """
    Delete a task.
    
    Args:
        task_id: The ID of the task to delete
    """
    try:
        # Send POST request to delete task
        response = requests.post(f"{FLASK_URL}/delete/{task_id}")
        
        if response.status_code == 200:
            return f"Task {task_id} deleted"
        else:
            return f"Error deleting task: HTTP {response.status_code}"
    except Exception as e:
        return f"Error deleting task: {str(e)}"

@mcp.tool()
def edit_task(task_id: int, new_text: str) -> str:
    """
    Edit a task's text.
    
    Args:
        task_id: The ID of the task to edit
        new_text: The new text for the task
    """
    try:
        # First get the edit page to simulate a browser
        response = requests.get(f"{FLASK_URL}/edit/{task_id}")
        
        # Then send POST request to update task
        response = requests.post(
            f"{FLASK_URL}/edit/{task_id}",
            data={"text": new_text},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return f"Task {task_id} updated to: {new_text}"
        else:
            return f"Error editing task: HTTP {response.status_code}"
    except Exception as e:
        return f"Error editing task: {str(e)}"

@mcp.tool()
def filter_tasks_by_context(context: str) -> str:
    """
    Filter tasks by context.
    
    Args:
        context: The context to filter by (without the @ symbol)
    """
    try:
        # Send GET request to filter tasks
        response = requests.get(f"{FLASK_URL}/filter?type=context&value={context}")
        
        if response.status_code != 200:
            return f"Error filtering tasks: HTTP {response.status_code}"
        
        # Parse HTML to extract filtered tasks (simplified approach)
        html = response.text
        
        # Extract tasks from the filtered view
        tasks_section = html.split('Active Tasks')[1].split('card-body')[1]
        tasks_items = re.findall(r'<li class="list-group-item.*?>(.*?)</li>', tasks_section, re.DOTALL)
        
        if not tasks_items or "No active tasks" in tasks_section:
            return f"No tasks found with context @{context}"
        
        # Format the output
        result = f"# Tasks with context @{context}:\n\n"
        for i, task_html in enumerate(tasks_items):
            # Extract task ID
            task_id = re.search(r'complete_task/(\d+)', task_html)
            if task_id:
                task_id = task_id.group(1)
                
            # Extract task text (simplified)
            task_text = re.sub(r'<.*?>', ' ', task_html)
            task_text = re.sub(r'\s+', ' ', task_text).strip()
            
            result += f"{i+1}. {task_text} (ID: {task_id})\n"
        
        return result
    except Exception as e:
        return f"Error filtering tasks by context: {str(e)}"

@mcp.tool()
def filter_tasks_by_project(project: str) -> str:
    """
    Filter tasks by project.
    
    Args:
        project: The project to filter by (without the + symbol)
    """
    try:
        # Send GET request to filter tasks
        response = requests.get(f"{FLASK_URL}/filter?type=project&value={project}")
        
        if response.status_code != 200:
            return f"Error filtering tasks: HTTP {response.status_code}"
        
        # Parse HTML to extract filtered tasks (simplified approach)
        html = response.text
        
        # Extract tasks from the filtered view
        tasks_section = html.split('Active Tasks')[1].split('card-body')[1]
        tasks_items = re.findall(r'<li class="list-group-item.*?>(.*?)</li>', tasks_section, re.DOTALL)
        
        if not tasks_items or "No active tasks" in tasks_section:
            return f"No tasks found with project +{project}"
        
        # Format the output
        result = f"# Tasks with project +{project}:\n\n"
        for i, task_html in enumerate(tasks_items):
            # Extract task ID
            task_id = re.search(r'complete_task/(\d+)', task_html)
            if task_id:
                task_id = task_id.group(1)
                
            # Extract task text (simplified)
            task_text = re.sub(r'<.*?>', ' ', task_html)
            task_text = re.sub(r'\s+', ' ', task_text).strip()
            
            result += f"{i+1}. {task_text} (ID: {task_id})\n"
        
        return result
    except Exception as e:
        return f"Error filtering tasks by project: {str(e)}"

# Prompts
@mcp.prompt()
def add_task_prompt() -> str:
    """Prompt for adding a new task"""
    return """
    I'll help you add a new task to your todo list.
    
    Please provide the task details in todo.txt format:
    - You can specify priority with (A), (B), (C), etc. at the beginning
    - Use @context to add contexts
    - Use +project to add projects
    
    For example: "(A) Call mom @phone +family" or "Buy groceries @errands +shopping"
    
    What task would you like to add?
    """

@mcp.prompt()
def manage_tasks_prompt() -> str:
    """Prompt for managing existing tasks"""
    return """
    I'll help you manage your todo list. Here are some things I can do:
    
    1. Show all tasks
    2. Show task details
    3. Complete a task
    4. Uncomplete a task
    5. Edit a task
    6. Delete a task
    7. Filter tasks by context or project
    
    What would you like to do?
    """

if __name__ == "__main__":
    mcp.run()
