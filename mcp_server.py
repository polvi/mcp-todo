from mcp.server.fastmcp import FastMCP
import requests

# Create an MCP server
mcp = FastMCP("Todo App Proxy")

# Base URL for the Flask app
BASE_URL = "http://localhost:5000"

@mcp.resource("tasks://all")
def get_all_tasks() -> str:
    """Get all tasks from the Flask app"""
    response = requests.get(f"{BASE_URL}/")
    return f"All tasks from the Todo app: {response.text}"

@mcp.resource("tasks://completed")
def get_completed_tasks() -> str:
    """Get completed tasks from the Flask app"""
    response = requests.get(f"{BASE_URL}/")
    return f"Completed tasks from the Todo app: {response.text}"

@mcp.resource("tasks://filter/{filter_type}/{filter_value}")
def filter_tasks(filter_type: str, filter_value: str) -> str:
    """Filter tasks by context or project"""
    response = requests.get(f"{BASE_URL}/filter?type={filter_type}&value={filter_value}")
    return f"Filtered tasks ({filter_type}:{filter_value}): {response.text}"

@mcp.tool()
def add_task(text: str) -> str:
    """Add a new task"""
    response = requests.post(f"{BASE_URL}/add", data={"text": text})
    return f"Task added: {text}"

@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as complete"""
    response = requests.post(f"{BASE_URL}/complete/{task_id}")
    return f"Task {task_id} marked as complete"

@mcp.tool()
def uncomplete_task(task_id: int) -> str:
    """Mark a task as incomplete"""
    response = requests.post(f"{BASE_URL}/uncomplete/{task_id}")
    return f"Task {task_id} marked as incomplete"

@mcp.tool()
def delete_task(task_id: int) -> str:
    """Delete a task"""
    response = requests.post(f"{BASE_URL}/delete/{task_id}")
    return f"Task {task_id} deleted"

@mcp.tool()
def edit_task(task_id: int, text: str) -> str:
    """Edit a task"""
    response = requests.post(f"{BASE_URL}/edit/{task_id}", data={"text": text})
    return f"Task {task_id} updated to: {text}"

if __name__ == "__main__":
    mcp.run()
