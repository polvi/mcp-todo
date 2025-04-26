from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'todo_secret_key'  # For flash messages

DATABASE = 'todo.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the tasks table"""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                priority TEXT,
                created_date TEXT,
                completed INTEGER DEFAULT 0,
                completed_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    """Display all tasks"""
    conn = get_db_connection()
    # Get incomplete tasks first, then completed tasks
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE completed = 0 ORDER BY '
        'CASE WHEN priority IS NULL THEN "Z" ELSE priority END, created_date'
    ).fetchall()
    
    completed_tasks = conn.execute(
        'SELECT * FROM tasks WHERE completed = 1 ORDER BY completed_date DESC'
    ).fetchall()
    
    conn.close()
    return render_template('index.html', tasks=tasks, completed_tasks=completed_tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Add a new task"""
    text = request.form.get('text', '').strip()
    
    if not text:
        flash('Task cannot be empty!', 'error')
        return redirect(url_for('index'))
    
    # Parse the task text for priority, projects, and contexts
    priority = None
    if len(text) >= 3 and text[0] == '(' and text[2] == ')' and text[1].isupper():
        priority = text[1]
        text = text[4:]  # Remove priority and following space
    
    # Add today's date
    created_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (text, priority, created_date, completed) VALUES (?, ?, ?, 0)',
                (text, priority, created_date))
    conn.commit()
    conn.close()
    
    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/complete/<int:id>', methods=['POST'])
def complete_task(id):
    """Mark a task as complete"""
    completed_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET completed = 1, completed_date = ? WHERE id = ?',
                (completed_date, id))
    conn.commit()
    conn.close()
    
    flash('Task completed!', 'success')
    return redirect(url_for('index'))

@app.route('/uncomplete/<int:id>', methods=['POST'])
def uncomplete_task(id):
    """Mark a task as incomplete"""
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET completed = 0, completed_date = NULL WHERE id = ?',
                (id,))
    conn.commit()
    conn.close()
    
    flash('Task marked as incomplete!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    """Delete a task"""
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Task deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    """Edit a task"""
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        
        if not text:
            flash('Task cannot be empty!', 'error')
            return redirect(url_for('edit_task', id=id))
        
        # Parse the task text for priority
        priority = None
        if len(text) >= 3 and text[0] == '(' and text[2] == ')' and text[1].isupper():
            priority = text[1]
            text = text[4:]  # Remove priority and following space
        
        conn.execute('UPDATE tasks SET text = ?, priority = ? WHERE id = ?',
                    (text, priority, id))
        conn.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    
    conn.close()
    return render_template('edit.html', task=task)

@app.route('/filter')
def filter_tasks():
    """Filter tasks by context or project"""
    filter_type = request.args.get('type')
    filter_value = request.args.get('value')
    
    conn = get_db_connection()
    
    if filter_type == 'context':
        search = f'% @{filter_value} %'
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE completed = 0 AND (text LIKE ? OR text LIKE ? OR text LIKE ?) '
            'ORDER BY CASE WHEN priority IS NULL THEN "Z" ELSE priority END, created_date',
            (f'% @{filter_value} %', f'% @{filter_value}', f'@{filter_value} %')
        ).fetchall()
    elif filter_type == 'project':
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE completed = 0 AND (text LIKE ? OR text LIKE ? OR text LIKE ?) '
            'ORDER BY CASE WHEN priority IS NULL THEN "Z" ELSE priority END, created_date',
            (f'% +{filter_value} %', f'% +{filter_value}', f'+{filter_value} %')
        ).fetchall()
    else:
        return redirect(url_for('index'))
    
    completed_tasks = []  # Don't show completed tasks in filtered view
    conn.close()
    
    return render_template('index.html', tasks=tasks, completed_tasks=completed_tasks, 
                          filter_active=True, filter_type=filter_type, filter_value=filter_value)

# API endpoints for MCP server
@app.route('/api/tasks/all', methods=['GET'])
def api_all_tasks():
    """Get all tasks formatted for MCP"""
    conn = get_db_connection()
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE completed = 0 ORDER BY '
        'CASE WHEN priority IS NULL THEN "Z" ELSE priority END, created_date'
    ).fetchall()
    
    result = "Active Tasks:\n"
    for task in tasks:
        priority_str = f" (Priority: {task['priority']})" if task['priority'] else ""
        result += f"{task['id']}. {task['text']}{priority_str}\n"
    
    conn.close()
    return result

@app.route('/api/tasks/completed', methods=['GET'])
def api_completed_tasks():
    """Get completed tasks formatted for MCP"""
    conn = get_db_connection()
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE completed = 1 ORDER BY completed_date DESC'
    ).fetchall()
    
    result = "Completed Tasks:\n"
    if not tasks:
        result += "No completed tasks found.\n"
    else:
        for task in tasks:
            result += f"{task['id']}. {task['text']}\n"
    
    conn.close()
    return result

@app.route('/api/tasks/filter', methods=['GET'])
def api_filter_tasks():
    """Filter tasks by context or project formatted for MCP"""
    filter_type = request.args.get('type')
    filter_value = request.args.get('value')
    
    conn = get_db_connection()
    
    if filter_type == 'context':
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE completed = 0 AND (text LIKE ? OR text LIKE ? OR text LIKE ?) '
            'ORDER BY CASE WHEN priority IS NULL THEN "Z" ELSE priority END, created_date',
            (f'% @{filter_value} %', f'% @{filter_value}', f'@{filter_value} %')
        ).fetchall()
    elif filter_type == 'project':
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE completed = 0 AND (text LIKE ? OR text LIKE ? OR text LIKE ?) '
            'ORDER BY CASE WHEN priority IS NULL THEN "Z" ELSE priority END, created_date',
            (f'% +{filter_value} %', f'% +{filter_value}', f'+{filter_value} %')
        ).fetchall()
    else:
        return f"Error: Invalid filter type '{filter_type}'"
    
    result = f"Filtered Tasks ({filter_type}: {filter_value}):\n"
    if not tasks:
        result += f"No tasks found for {filter_type}: {filter_value}\n"
    else:
        for task in tasks:
            priority_str = f" (Priority: {task['priority']})" if task['priority'] else ""
            result += f"{task['id']}. {task['text']}{priority_str}\n"
    
    conn.close()
    return result

@app.route('/api/task/add', methods=['POST'])
def api_add_task():
    """Add a task and return formatted response for MCP"""
    text = request.form.get('text', '').strip()
    
    if not text:
        return "Error: Task text cannot be empty"
    
    # Parse the task text for priority
    priority = None
    if len(text) >= 3 and text[0] == '(' and text[2] == ')' and text[1].isupper():
        priority = text[1]
        text = text[4:]  # Remove priority and following space
    
    # Add today's date
    created_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO tasks (text, priority, created_date, completed) VALUES (?, ?, ?, 0)',
                (text, priority, created_date))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return f"Task added: {text}"

@app.route('/api/task/complete/<int:id>', methods=['POST'])
def api_complete_task(id):
    """Complete a task and return formatted response for MCP"""
    completed_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET completed = 1, completed_date = ? WHERE id = ?',
                (completed_date, id))
    conn.commit()
    conn.close()
    
    return f"Task {id} marked as complete"

@app.route('/api/task/uncomplete/<int:id>', methods=['POST'])
def api_uncomplete_task(id):
    """Uncomplete a task and return formatted response for MCP"""
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET completed = 0, completed_date = NULL WHERE id = ?',
                (id,))
    conn.commit()
    conn.close()
    
    return f"Task {id} marked as incomplete"

@app.route('/api/task/delete/<int:id>', methods=['POST'])
def api_delete_task(id):
    """Delete a task and return formatted response for MCP"""
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return f"Task {id} deleted"

@app.route('/api/task/edit/<int:id>', methods=['POST'])
def api_edit_task(id):
    """Edit a task and return formatted response for MCP"""
    text = request.form.get('text', '').strip()
    
    if not text:
        return "Error: Task text cannot be empty"
    
    # Parse the task text for priority
    priority = None
    if len(text) >= 3 and text[0] == '(' and text[2] == ')' and text[1].isupper():
        priority = text[1]
        text = text[4:]  # Remove priority and following space
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET text = ?, priority = ? WHERE id = ?',
                (text, priority, id))
    conn.commit()
    conn.close()
    
    return f"Task {id} updated to: {text}"

if __name__ == '__main__':
    app.run(debug=True)
