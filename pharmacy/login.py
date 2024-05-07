import tkinter as tk
import sqlite3
import hashlib
from tkinter import messagebox


def create_login_window(main_app):
    login_window = tk.Tk()
    login_window.title("Login System")
    login_window.geometry("350x200")

    frame = tk.Frame(login_window)
    frame.pack(padx=10, pady=10)

    username_label = tk.Label(frame, text="Username")
    username_label.grid(row=0, column=0, padx=10, pady=10)

    username_entry = tk.Entry(frame)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    password_label = tk.Label(frame, text="Password")
    password_label.grid(row=1, column=0, padx=10, pady=10)

    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    login_button = tk.Button(frame, text="Login", command=lambda: login(login_window, main_app, username_entry,
                                                                        password_entry))
    login_button.grid(row=2, column=0, padx=10, pady=10)

    exit_button = tk.Button(frame, text="Exit", command=login_window.destroy)
    exit_button.grid(row=2, column=1, padx=10, pady=10)

    return login_window


# add  logic to check the username and password
def login(login_window, main_app, username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    # Connect to the SQLite database
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    # Query the database for the user
    cursor.execute('''SELECT password, salt FROM users WHERE username = ?''', (username,))
    result = cursor.fetchone()

    # If the user exists
    if result is not None:
        stored_password, salt = result

        # Hash the entered password with the stored salt
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        # If the hashed password matches the stored password
        if hashed_password == stored_password:
            login_window.destroy()
            main_app.deiconify()
        else:
            messagebox.showerror("Login", "Invalid username or password")
    else:
        messagebox.showerror("Login", "Invalid username or password")
