"""
TaskFlow - Modern Task Management System
A responsive Flask-based task management application with modern UI design.

Features:
- Create, edit, delete tasks
- Mark tasks as complete/incomplete
- Real-time analytics dashboard
- Responsive design for all devices
- Modern UI with animations
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import tempfile

app = Flask(__name__)
# Use environment variable for secret key in production, fallback for development
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration - use temp directory for serverless deployment
if os.environ.get('VERCEL'):
    # In Vercel serverless environment, use /tmp directory
    DATABASE = os.path.join('/tmp', 'tasks.db')
else:
    # Local development
    DATABASE = os.path.join('instance', 'tasks.db')
    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Main page showing all tasks with analytics"""
    conn = get_db_connection()

    # Get all tasks
    tasks = conn.execute(
        'SELECT * FROM tasks ORDER BY created_at DESC'
    ).fetchall()

    # Calculate analytics
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task['completed']])
    pending_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    conn.close()

    return render_template('index.html',
                         tasks=tasks,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         pending_tasks=pending_tasks,
                         completion_rate=completion_rate)

@app.route('/add', methods=['POST'])
def add_task():
    """Add a new task"""
    title = request.form.get('title')
    description = request.form.get('description', '')

    if not title:
        flash('Task title is required!', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO tasks (title, description) VALUES (?, ?)',
        (title, description)
    )
    conn.commit()
    conn.close()

    flash('Task added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    """Mark a task as completed"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE tasks SET completed = 1 WHERE id = ?',
        (task_id,)
    )
    conn.commit()
    conn.close()

    flash('Task marked as completed!', 'success')
    return redirect(url_for('index'))

@app.route('/uncomplete/<int:task_id>')
def uncomplete_task(task_id):
    """Mark a task as not completed"""
    conn = get_db_connection()
    conn.execute(
        'UPDATE tasks SET completed = 0 WHERE id = ?',
        (task_id,)
    )
    conn.commit()
    conn.close()

    flash('Task marked as incomplete!', 'info')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Delete a task"""
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/api/tasks')
def api_tasks():
    """API endpoint to get all tasks as JSON"""
    conn = get_db_connection()
    tasks = conn.execute(
        'SELECT * FROM tasks ORDER BY created_at DESC'
    ).fetchall()
    conn.close()

    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task['id'],
            'title': task['title'],
            'description': task['description'],
            'completed': bool(task['completed']),
            'created_at': task['created_at']
        })

    return jsonify(tasks_list)

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    app.run(debug=True)
