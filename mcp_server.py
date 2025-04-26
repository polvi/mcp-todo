from mcp.server.fastmcp import FastMCP, Context
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mcp_server')

# Create an MCP server
mcp = FastMCP("Todo App Proxy")

@mcp.resource("tasks://all")
def get_all_tasks() -> str:
    """Get all tasks"""
    return """
    Task List:
    1. Buy groceries (Priority: A)
    2. Finish project report
    3. Call dentist for appointment
    4. Prepare presentation for meeting
    """

@mcp.resource("tasks://completed")
def get_completed_tasks() -> str:
    """Get completed tasks"""
    return """
    Completed Tasks:
    1. Pay electricity bill
    2. Send birthday card to mom
    3. Update resume
    """

@mcp.resource("tasks://filter/{filter_type}/{filter_value}")
def filter_tasks(filter_type: str, filter_value: str) -> str:
    """Filter tasks by context or project"""
    if filter_type == "context" and filter_value == "home":
        return """
        Home Tasks:
        1. Clean garage
        2. Fix leaky faucet
        3. Organize bookshelf
        """
    elif filter_type == "project" and filter_value == "work":
        return """
        Work Project Tasks:
        1. Complete quarterly report
        2. Schedule team meeting
        3. Review budget proposal
        """
    else:
        return f"No tasks found for {filter_type}: {filter_value}"

@mcp.tool()
def add_task(text: str, ctx: Context = None) -> str:
    """Add a new task"""
    logger.info(f"Adding task: {text}")
    return f"Task added: {text}"

@mcp.tool()
def complete_task(task_id: int, ctx: Context = None) -> str:
    """Mark a task as complete"""
    logger.info(f"Completing task: {task_id}")
    return f"Task {task_id} marked as complete"

@mcp.tool()
def uncomplete_task(task_id: int, ctx: Context = None) -> str:
    """Mark a task as incomplete"""
    logger.info(f"Uncompleting task: {task_id}")
    return f"Task {task_id} marked as incomplete"

@mcp.tool()
def delete_task(task_id: int, ctx: Context = None) -> str:
    """Delete a task"""
    logger.info(f"Deleting task: {task_id}")
    return f"Task {task_id} deleted"

@mcp.tool()
def edit_task(task_id: int, text: str, ctx: Context = None) -> str:
    """Edit a task"""
    logger.info(f"Editing task {task_id} to: {text}")
    return f"Task {task_id} updated to: {text}"

@mcp.tool()
def debug_info() -> str:
    """Get debug information about the MCP server"""
    logger.info("Debug info requested")
    return """
    MCP Server Information:
    - Name: Todo App Proxy
    - Available resources:
      * tasks://all
      * tasks://completed
      * tasks://filter/{filter_type}/{filter_value}
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
