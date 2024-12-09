import tkinter as tk
from tkinter import messagebox, font
import datetime
import json
import os
import smtplib
import pandas as pd
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Main window setup
root = tk.Tk()
root.configure(bg="#f5f5f5")
root.title("To-Do List")
root.geometry("650x750")

# Global settings for fonts
title_font = font.Font(family="Helvetica", size=16, weight="bold")
label_font = font.Font(family="Helvetica", size=12)
button_font = font.Font(family="Helvetica", size=10, weight="bold")

# Task storage 
tasks = []
tasks_df = pd.DataFrame(columns=["name", "deadline", "priority", "completed", "added_time", "completed_time", "category"])

# Load tasks from file (Persistence)
def load_tasks():
    """Load tasks from a file, or create an empty list if no file exists."""
    global tasks, tasks_df
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
            # Ensure all tasks have a 'category' key
            for task in tasks:
                if "category" not in task:
                    task["category"] = "Uncategorized"
    if os.path.exists("tasks.csv"):
        tasks_df = pd.read_csv("tasks.csv", parse_dates=["added_time", "completed_time"])
        # Ensure all tasks in DataFrame have a 'category' column
        if 'category' not in tasks_df.columns:
            tasks_df['category'] = "Uncategorized"
    update_listbox()

# Save tasks to file (Persistence)
def save_tasks():
    """Save the current tasks to a file and CSV for analysis."""
    with open("tasks.json", "w") as file:
        json.dump(tasks, file)
    tasks_df.to_csv("tasks.csv", index=False)

# Update the listbox display with tasks
def update_listbox():
    """Refresh the listbox display with all tasks, showing priority, due date, and overdue status if applicable."""
    clear_listbox()
    for task in tasks:
        status = "✓" if task["completed"] else "✗"
        overdue = ""
        task_due = datetime.datetime.strptime(task["deadline"], "%Y-%m-%d")
        if not task["completed"] and task_due < datetime.datetime.now():
            overdue = " - Overdue!"
        lb_tasks.insert("end",
                          f"{status} {task['name']} (Priority: {task['priority']}) - Due: {task['deadline']} - Category: {task['category']}{overdue}")

# Clear listbox
def clear_listbox():
    """Clear all entries in the task listbox."""
    lb_tasks.delete(0, "end")

# Add a new task or update the selected task
def add_task():
    """Add a new task or update the selected task with a name, deadline, and priority."""
    global tasks_df
    task_name = txt_input.get().strip()
    deadline = txt_deadline.get().strip()
    priority = priority_var.get()
    category = category_var.get()

    if not task_name or not deadline:
        messagebox.showwarning("Warning", "Please enter task name and deadline.")
        return

    try:
        deadline_date = datetime.datetime.strptime(deadline, "%Y-%m-%d")
        if deadline_date < datetime.datetime.now():
            messagebox.showwarning("Invalid Deadline", "Deadline must be a future date.")
            return
    except ValueError:
        messagebox.showwarning("Warning", "Please enter a valid date in YYYY-MM-DD format.")
        return

    # Default category if not selected
    if not category:
        category = "Uncategorized"

    # Check if we are editing an existing task or adding a new one
    if hasattr(add_task, "edit_index") and add_task.edit_index is not None:
        # Editing existing task
        task = tasks[add_task.edit_index]
        task["name"] = task_name
        task["deadline"] = deadline
        task["priority"] = priority
        task["category"] = category  # Ensure category is updated
        tasks_df.loc[add_task.edit_index, "name"] = task_name
        tasks_df.loc[add_task.edit_index, "deadline"] = deadline
        tasks_df.loc[add_task.edit_index, "priority"] = priority
        tasks_df.loc[add_task.edit_index, "category"] = category  # Ensure category is updated

        messagebox.showinfo("Info", f"Task '{task_name}' updated.")
        add_task.edit_index = None  # Clear the edit mode
    else:
        # Adding new task
        added_time = datetime.datetime.now()
        tasks.append({"name": task_name, "deadline": deadline, "priority": priority, "completed": False, "category": category})
        tasks_df = pd.concat([tasks_df, pd.DataFrame(
            {"name": [task_name], "deadline": [deadline], "priority": [priority], "completed": [False],
             "added_time": [added_time], "completed_time": [None], "category": [category]})], ignore_index=True)

        messagebox.showinfo("Info", f"Task '{task_name}' added.")

    # Clear input fields and update the task list
    txt_input.delete(0, "end")
    txt_deadline.delete(0, "end")
    save_tasks()
    update_listbox()

# Edit task function
def edit_task():
    """Edit the selected task by filling the fields with its current data."""
    try:
        selected_index = lb_tasks.curselection()[0]
        task = tasks[selected_index]

        # Fill input fields with task details
        txt_input.delete(0, tk.END)
        txt_input.insert(0, task["name"])
        txt_deadline.delete(0, tk.END)
        txt_deadline.insert(0, task["deadline"])
        priority_var.set(task["priority"])
        category_var.set(task["category"])

        # Store the index of the task to be edited
        add_task.edit_index = selected_index

    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to edit.")

# Mark task as completed
def mark_completed():
    """Mark the selected task as completed and record completion time in the DataFrame."""
    global tasks_df
    try:
        selected_index = lb_tasks.curselection()[0]
        tasks[selected_index]["completed"] = True
        tasks_df.loc[selected_index, "completed"] = True
        tasks_df.loc[selected_index, "completed_time"] = datetime.datetime.now()

        save_tasks()
        update_listbox()
        messagebox.showinfo("Info", "Task marked as completed.")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to mark as completed.")

# Delete task
def delete_task():
    """Delete the selected task."""
    try:
        selected_index = lb_tasks.curselection()[0]
        tasks.pop(selected_index)
        tasks_df.drop(selected_index, inplace=True)

        save_tasks()
        update_listbox()
        messagebox.showinfo("Info", "Task deleted.")
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to delete.")

# Delay analysis
def analyze_delays():
    """Analyze tasks that were delayed and give a detailed report."""
    overdue_tasks = tasks_df[tasks_df['completed'] == False]
    overdue_tasks['deadline'] = pd.to_datetime ( overdue_tasks['deadline'] )
    overdue_tasks['is_overdue'] = overdue_tasks['deadline'] < datetime.datetime.now ()

    # Calculate delay (in days)
    overdue_tasks['delay'] = (datetime.datetime.now () - overdue_tasks['deadline']).dt.days
    overdue_tasks = overdue_tasks[overdue_tasks['is_overdue']]  # Filter only overdue tasks

    # Total overdue count
    overdue_count = overdue_tasks.shape[0]
    overdue_report = f"Overdue Tasks: {overdue_count}\n\n"

    if overdue_count > 0:
        # Display task name, deadline, priority, and category for each overdue task
        overdue_report += overdue_tasks[["name", "deadline", "priority", "category"]].to_string ( index=False )

        # Count of overdue tasks by Category (Personal, Study, etc.)
        category_count = overdue_tasks.groupby ( 'category' ).size ().sort_values ( ascending=False )
        overdue_report += "\n\nOverdue Tasks Count by Category:\n"
        for category in category_count.index:
            overdue_report += f"{category}: {category_count[category]}\n"

        # Study Category: Further breakdown for delayed study tasks
        study_tasks = overdue_tasks[overdue_tasks['category'] == 'Study']
        if not study_tasks.empty:
            # Get the top 3 most delayed tasks within Study category by count
            study_task_counts = study_tasks['name'].value_counts ().head ( 3 )
            overdue_report += "\n\nTop 3 Delayed Study Tasks (by count):\n"
            for task_name, count in study_task_counts.items ():
                overdue_report += f"{task_name}: {count} tasks\n"

    else:
        overdue_report += "No overdue tasks."

    messagebox.showinfo ( "Overdue Task Analysis", overdue_report )
# Import tasks from CSV file
def import_tasks():
    """Import tasks from a CSV file."""
    filename = askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if filename:
        global tasks_df
        tasks_df = pd.read_csv(filename)
        # Assuming the CSV file has columns like 'name', 'deadline', 'priority', etc.
        messagebox.showinfo("Info", f"Tasks imported from {filename}")
        save_tasks()
        update_listbox()

# Export tasks to CSV
def export_tasks():
    """Export current tasks to a CSV file."""
    filename = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if filename:
        tasks_df.to_csv(filename, index=False)
        messagebox.showinfo("Info", f"Tasks exported to {filename}")

# GUI Components
title_label = tk.Label(root, text="To-Do List App", font=title_font, bg="#f5f5f5")
title_label.pack(pady=10)

# Task Name Label and Entry
task_name_label = tk.Label ( root, text="Task Name:", font=label_font, bg="#f5f5f5" )
task_name_label.pack ( pady=2 )
txt_input = tk.Entry(root, font=label_font, width=40)
txt_input.pack(pady=5)

# Deadline Label and Entry
deadline_label = tk.Label ( root, text="Deadline (YYYY-MM-DD):", font=label_font, bg="#f5f5f5" )
deadline_label.pack ( pady=2 )
txt_deadline = tk.Entry(root, font=label_font, width=40)
txt_deadline.pack(pady=5)

priority_label = tk.Label ( root, text="Priority:", font=label_font, bg="#f5f5f5" )
priority_label.pack ( pady=2 )
priority_var = tk.StringVar()
priority_menu = tk.OptionMenu(root, priority_var, "High", "Medium", "Low")
priority_menu.config(font=label_font)
priority_menu.pack(pady=5)

category_label = tk.Label ( root, text="Category:", font=label_font, bg="#f5f5f5" )
category_label.pack ( pady=2 )
category_var = tk.StringVar()
category_menu = tk.OptionMenu(root, category_var, "Work", "Personal", "Study", "Other")
category_menu.config(font=label_font)
category_menu.pack(pady=5)

# Buttons
button_add = tk.Button(root, text="Add/Update Task", font=button_font, command=add_task)
button_add.pack(pady=5)

button_edit = tk.Button(root, text="Edit Task", font=button_font, command=edit_task)
button_edit.pack(pady=5)

button_complete = tk.Button(root, text="Mark as Completed", font=button_font, command=mark_completed)
button_complete.pack(pady=5)

button_delete = tk.Button(root, text="Delete Task", font=button_font, command=delete_task)
button_delete.pack(pady=5)

button_analyze = tk.Button(root, text="Analyze Delays", font=button_font, command=analyze_delays)
button_analyze.pack(pady=5)

button_import = tk.Button(root, text="Import Tasks", font=button_font, command=import_tasks)
button_import.pack(pady=5)

button_export = tk.Button(root, text="Export Tasks", font=button_font, command=export_tasks)
button_export.pack(pady=5)

lb_tasks = tk.Listbox(root, font=label_font, height=15, width=80)
lb_tasks.pack(pady=10)


# Load tasks
load_tasks()

# Run the GUI
root.mainloop()
