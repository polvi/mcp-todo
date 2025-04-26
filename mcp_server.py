from mcp.server.fastmcp import FastMCP, Context
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp_server')

# Flask app configuration
FLASK_BASE_URL = "http://127.0.0.1:5000"

# Create an MCP server
mcp = FastMCP("Todo App Proxy", 
              description="A proxy to the Todo Flask application",
              dependencies=["requests"])

@mcp.resource("tasks://all")
def get_all_tasks() -> str:
    """Get all tasks from the Flask app"""
    logger.info("Resource requested: tasks://all")
    try:
        logger.info(f"Sending request to {FLASK_BASE_URL}/api/tasks/all")
        response = requests.get(f"{FLASK_BASE_URL}/api/tasks/all")
        logger.info(f"Response status: {response.status_code}")
        if response.status_code == 200:
            return response.text
        else:
            error_msg = f"Error: Flask app returned status code {response.status_code}"
            logger.error(f"{error_msg}, Response: {response.text}")
            return error_msg
    except Exception as e:
        logger.error(f"Error getting all tasks: {str(e)}")
        return f"Error retrieving tasks: {str(e)}"

@mcp.resource("tasks://completed")
def get_completed_tasks() -> str:
    """Get completed tasks from the Flask app"""
    logger.info("Resource requested: tasks://completed")
    try:
        response = requests.get(f"{FLASK_BASE_URL}/api/tasks/completed")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: Flask app returned status code {response.status_code}"
    except Exception as e:
        logger.error(f"Error getting completed tasks: {str(e)}")
        return f"Error retrieving completed tasks: {str(e)}"

@mcp.resource("tasks://filter/{filter_type}/{filter_value}")
def filter_tasks(filter_type: str, filter_value: str) -> str:
    """Filter tasks by context or project from the Flask app"""
    logger.info(f"Resource requested: tasks://filter/{filter_type}/{filter_value}")
    try:
        response = requests.get(f"{FLASK_BASE_URL}/api/tasks/filter?type={filter_type}&value={filter_value}")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: Flask app returned status code {response.status_code}"
    except Exception as e:
        logger.error(f"Error filtering tasks: {str(e)}")
        return f"Error filtering tasks: {str(e)}"

@mcp.tool()
def add_task(text: str, ctx: Context = None) -> str:
    """Add a new task via the Flask app"""
    logger.info(f"Adding task: {text}")
    try:
        response = requests.post(f"{FLASK_BASE_URL}/api/task/add", data={"text": text})
        if response.status_code == 200:
            return response.text
        else:
            error_msg = f"Error: Flask app returned status code {response.status_code}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error adding task: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def complete_task(task_id: int, ctx: Context = None) -> str:
    """Mark a task as complete via the Flask app"""
    logger.info(f"Completing task: {task_id}")
    try:
        response = requests.post(f"{FLASK_BASE_URL}/api/task/complete/{task_id}")
        if response.status_code == 200:
            return response.text
        else:
            error_msg = f"Error: Flask app returned status code {response.status_code}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error completing task: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def uncomplete_task(task_id: int, ctx: Context = None) -> str:
    """Mark a task as incomplete via the Flask app"""
    logger.info(f"Uncompleting task: {task_id}")
    try:
        response = requests.post(f"{FLASK_BASE_URL}/api/task/uncomplete/{task_id}")
        if response.status_code == 200:
            return response.text
        else:
            error_msg = f"Error: Flask app returned status code {response.status_code}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error uncompleting task: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def delete_task(task_id: int, ctx: Context = None) -> str:
    """Delete a task via the Flask app"""
    logger.info(f"Deleting task: {task_id}")
    try:
        response = requests.post(f"{FLASK_BASE_URL}/api/task/delete/{task_id}")
        if response.status_code == 200:
            return response.text
        else:
            error_msg = f"Error: Flask app returned status code {response.status_code}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error deleting task: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def edit_task(task_id: int, text: str, ctx: Context = None) -> str:
    """Edit a task via the Flask app"""
    logger.info(f"Editing task {task_id} to: {text}")
    try:
        response = requests.post(f"{FLASK_BASE_URL}/api/task/edit/{task_id}", data={"text": text})
        if response.status_code == 200:
            return response.text
        else:
            error_msg = f"Error: Flask app returned status code {response.status_code}"
            logger.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = f"Error editing task: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def debug_info() -> str:
    """Get debug information about the MCP server"""
    logger.info("Debug info requested")
    try:
        # Check if Flask app is running
        logger.info(f"Testing connection to Flask app at {FLASK_BASE_URL}")
        response = requests.get(f"{FLASK_BASE_URL}")
        flask_status = f"Online (status: {response.status_code})"
        
        # Try API endpoint
        api_response = requests.get(f"{FLASK_BASE_URL}/api/tasks/all")
        api_status = f"API status: {api_response.status_code}"
        if api_response.status_code != 200:
            api_status += f", Response: {api_response.text[:100]}"
    except Exception as e:
        flask_status = f"Offline: {str(e)}"
        api_status = "Not available"
    
    return f"""
    MCP Server Information:
    - Name: Todo App Proxy
    - Flask App Status: {flask_status}
    - API Status: {api_status}
    - Flask App URL: {FLASK_BASE_URL}
    - Available resources:
      * tasks://all
      * tasks://completed
      * tasks://filter/{{filter_type}}/{{filter_value}}
    - Available tools:
      * add_task(text)
      * complete_task(task_id)
      * uncomplete_task(task_id)
      * delete_task(task_id)
      * edit_task(task_id, text)
      * debug_info()
    """

if __name__ == "__main__":
    logger.info("Starting MCP server")
    mcp.run()

# Example usage:
# - Get all tasks: tasks://all
# - Get completed tasks: tasks://completed
# - Filter tasks: tasks://filter/context/home or tasks://filter/project/work
# - Add task: add_task("Buy milk")
# - Complete task: complete_task(1)
# - Uncomplete task: uncomplete_task(2)
# - Delete task: delete_task(3)
# - Edit task: edit_task(4, "New task description")
