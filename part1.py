import tkinter as tk
import random

# Create a window
root = tk.Tk()

#change root window background color
root.configure(bg="white")

#change the title
root.title("My Super Awesome To-Do List App")

#change the window size
root.geometry("200x500")

#create empty list
tasks = []

#For testing purposes use a default list
tasks = ["Call mom", "Buy a new phone", "Eat dinner", "Go to sleep"]

#create functions

def update_listbox():
    #populate the listbox
    for task in tasks:
        lb_tasks.insert("end", task) #insert each task into the listbox at the end

def clear_listbox():
    lb_tasks.delete(0, "end") #delete all tasks in the listbox from start to end

def add_task():
    #clear the current list
    clear_listbox()
    #get the task to add
    update_listbox()

def del_all():
    pass

def del_one():
    pass

def choose_random():
    pass

def show_number_of_tasks():
    pass

def sort_asc():
    pass

def sort_desc():
    pass

def exit():
    pass




# create gui
lbl_title = tk.Label(root, text="To-Do-List", bg="white")
lbl_title.pack()

lbl_display = tk.Label(root, text="", bg="white")
lbl_display.pack()

txt_input = tk.Entry(root, width=15)
txt_input.pack()

btn_add_task = tk.Button(root, text="Add Task", fg = "green", bg="white", command = add_task)
btn_add_task.pack()

btn_del_all = tk.Button(root, text="Delete All", fg = "green", bg="white", command = del_all)
btn_del_all.pack()

btn_del_one= tk.Button(root, text="Delete", fg = "green", bg="white", command = del_one )
btn_del_one.pack()

btn_sort_asc = tk.Button(root, text="Sort (ASC)", fg = "green", bg="white", command = sort_asc)
btn_sort_asc.pack()

btn_sort_desc = tk.Button(root, text="Sort (DESC)", fg = "green", bg="white", command = sort_desc)
btn_sort_desc.pack()

btn_choose_random = tk.Button(root, text="Choose Random", fg = "green", bg="white", command = choose_random)
btn_choose_random.pack()

btn_number_of_tasks = tk.Button(root, text="Number of Tasks", fg = "green", bg="white", command = show_number_of_tasks)
btn_number_of_tasks.pack()

btn_quit = tk.Button(root, text="Exit", fg = "green", bg="white", command = exit) #quit is a built-in function
btn_quit.pack()

lb_tasks = tk.Listbox(root) # Create a listbox widget
lb_tasks.pack() # Make the listbox fill
# the lb_tasks listbox widget is being packed into its parent widget using the pack() geometry manager. The parent widget for lb_tasks is root, which is the main window of the application created using tk.Tk().


root.mainloop() # Start the main event loop
