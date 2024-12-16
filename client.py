import socket
import threading
import pyaudio
import opus
import tkinter as tk
from tkinter import messagebox
import time
import hashlib
import bcrypt
import json
import os
from shared.voice_streaming import send_audio, receive_audio
from shared.user_db import authenticate_user, create_user
import shared.config as config

class VOIPClient:
    def __init__(self, root):
        self.root = root
        self.root.title("VOIP Client")
        self.root.geometry("400x400")
        self.username = None
        self.password = None
        self.server_socket = None
        self.calling = False
        self.client_addr = None
        self.is_connected = False

        self.create_login_gui()

    def create_login_gui(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, columnspan=2)

        self.signup_button = tk.Button(self.login_frame, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=3, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            self.username = username
            self.password = password
            if self.authenticate_user():
                self.create_call_gui()
                self.connect_to_server()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials.")
        else:
            messagebox.showwarning("Input Error", "Please fill in both fields.")

    def authenticate_user(self):
        return authenticate_user(self.username, self.password)

    def signup(self):
        def submit_signup():
            username = signup_username_entry.get()
            password = signup_password_entry.get()

            if username and password:
                if self.check_username_exists(username):
                    messagebox.showerror("Signup Error", "Username already exists.")
                else:
                    self.create_user(username, password)
                    messagebox.showinfo("Signup Success", "User registered successfully!")
                    signup_window.destroy()

        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")

        signup_username_label = tk.Label(signup_window, text="Username:")
        signup_username_label.pack()
        signup_username_entry = tk.Entry(signup_window)
        signup_username_entry.pack()

        signup_password_label = tk.Label(signup_window, text="Password:")
        signup_password_label.pack()
        signup_password_entry = tk.Entry(signup_window, show="*")
        signup_password_entry.pack()

        signup_button = tk.Button(signup_window, text="Create Account", command=submit_signup)
        signup_button.pack()

    def check_username_exists(self, username):
        # Check if the username already exists in the database
        return False  # Mock function for the sake of demonstration

    def create_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        create_user(username, hashed_password.decode())

    def create_call_gui(self):
        self.login_frame.destroy()

        self.call_frame = tk.Frame(self.root)
        self.call_frame.pack(pady=20)

        self.status_label = tk.Label(self.call_frame, text=f"Logged in as {self.username}", font=("Arial", 14))
        self.status_label.grid(row=0, columnspan=2)

        self.call_button = tk.Button(self.call_frame, text="Start Call", command=self.start_call)
        self.call_button.grid(row=1, column=0)

        self.end_call_button = tk.Button(self.call_frame, text="End Call", command=self.end_call)
        self.end_call_button.grid(row=1, column=1)

        self.mute_button = tk.Button(self.call_frame, text="Mute", command=self.mute)
        self.mute_button.grid(row=2, column=0)

    def connect_to_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(("localhost", 5001))

        message = json.dumps({"username": self.username, "password": self.password}).encode()
        self.server_socket.sendto(message, (config.HOST, config.PORT))

        response, _ = self.server_socket.recvfrom(1024)
        if response.decode() == "authenticated":
            self.is_connected = True
            threading.Thread(target=self.receive_audio).start()

    def start_call(self):
        if not self.is_connected:
            messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        self.calling = True
        self.client_addr = ("localhost", 5002)  # Mock address for the second client
        threading.Thread(target=self.send_audio, args=(self.client_addr,)).start()

    def send_audio(self, addr):
        send_audio(self.server_socket, addr, self.calling)

    def receive_audio(self):
        receive_audio(self.server_socket, self.client_addr)

    def end_call(self):
        self.calling = False
        self.client_addr = None
        messagebox.showinfo("Call Ended", "The call has been ended.")

    def mute(self):
        # Mute functionality - can be integrated with audio input processing
        messagebox.showinfo("Mute", "The call has been muted.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VOIPClient(root)
    root.mainloop()
