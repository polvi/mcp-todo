# Todo.txt Flask App with MCP Integration

A simple Flask application for managing todo.txt style task lists with Model Context Protocol (MCP) integration for AI assistants.

## Features

- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Priority support (A-Z)
- Context support (@context)
- Project support (+project)
- Filter tasks by context or project
- AI assistant integration via MCP

## Quick Start

### Installation

1. Clone this repository
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

### Running the Flask App

Start the Flask web application:
```
python app.py
```
Access the web interface at http://127.0.0.1:5000


### Testing with MCP Dev Tool

In a separate terminal (flask app must be running), test the MCP server with the development tool:
```
mcp dev mcp_server.py
```

### Installing in Claude Desktop

To use with Claude Desktop:
```
mcp install mcp_server.py
```
