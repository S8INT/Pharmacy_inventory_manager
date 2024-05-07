import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import os


class Login(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Login System")
        self.geometry("350x250")

        # create a login form inside a frame
        self.frame = tk.Frame(self)
        self.frame.pack(padx=10, pady=10)

        # create a label and entry for username
        self.label = tk.Label(self.frame, text="Username")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        self.username = tk.Entry(self.frame)
        self.username.grid(row=0, column=1, padx=10, pady=10)

        self.label = tk.Label(self.frame, text="Password")
        self.label.grid(row=1, column=0, padx=10, pady=10)

        self.password = tk.Entry(self.frame, show="*")
        self.password.grid(row=1, column=1, padx=10, pady=10)

        self.label = tk.Label(self.frame, text="Confirm Password")
        self.label.grid(row=2, column=0, padx=10, pady=10)

        self.confirm_password = tk.Entry(self.frame, show="*")
        self.confirm_password.grid(row=2, column=1, padx=10, pady=10)

        self.button = tk.Button(self.frame, text="Register", command=self.register_user)
        self.button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.db = sqlite3.connect('users.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                               (username TEXT PRIMARY KEY, password TEXT, salt TEXT, failed_attempts INTEGER)''')
        self.db.commit()

    def register_user(self):
        username = self.username.get()
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        if password != confirm_password:
            messagebox.showerror("Registration", "Passwords do not match")
            return

        salt = os.urandom(32)
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        try:
            self.cursor.execute('''INSERT INTO users (username, password, salt, failed_attempts)
                                    VALUES (?, ?, ?, ?)''', (username, hashed_password, salt, 0))
            self.db.commit()
            messagebox.showinfo("Registration", "Registration successful")
        except sqlite3.IntegrityError:
            messagebox.showerror("Registration", "Username already exists")
        except Exception as e:
            messagebox.showerror("Registration", f"An error occurred: {e}")

if __name__ == "__main__":
    app = Login()
    app.mainloop()
