# Collaborative Todo.txt Flask App

A simple Flask application that allows multiple users to collaborate on todo.txt style task lists.

## Features

- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Priority support (A-Z)
- Context support (@context)
- Project support (+project)
- Filter tasks by context or project
- Creation and completion dates tracking
- Simple, responsive UI

## Installation

1. Clone this repository
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your browser and navigate to `http://127.0.0.1:5000`

## Todo.txt Format

This application follows the todo.txt format:

- A single line represents a single task
- Priority is indicated with (A), (B), etc. at the beginning of the task
- Contexts are indicated with @context
- Projects are indicated with +project
- Creation date is automatically added
- Completion date is automatically added when a task is marked complete

## Usage

- Click on contexts (@context) or projects (+project) to filter tasks
- Use the "Add Task" form to create new tasks
- Use the "Complete" button to mark tasks as done
- Use the "Edit" button to modify tasks
- Use the "Delete" button to remove tasks

## License

MIT
