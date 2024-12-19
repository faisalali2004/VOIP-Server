import tkinter as tk
from tkinter import messagebox

# Helper function to create rounded buttons
def create_rounded_button(parent, text, command):
    button = tk.Button(parent, text=text, command=command, relief="flat", font=("Arial", 14),
                       bg="#4b0079", fg="white", width=20, height=2, bd=0, highlightthickness=0)
    button.config(borderwidth=0, highlightbackground="#4b0079", highlightcolor="#4b0079")
    button.pack(pady=10)
    return button

# Login UI
def create_login_gui(root, login_callback, signup_callback):
    login_frame = tk.Frame(root, bg="#f0f0f0")
    login_frame.pack(fill="both", expand=True)

    title = tk.Label(login_frame, text="VOIP Login", font=("Arial", 24), bg="#f0f0f0", fg="#4b0079")
    title.pack(pady=50)

    username_label = tk.Label(login_frame, text="Username", font=("Arial", 16), bg="#f0f0f0", fg="#4b0079")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_frame, font=("Arial", 14), bd=2)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_frame, text="Password", font=("Arial", 16), bg="#f0f0f0", fg="#4b0079")
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_frame, font=("Arial", 14), show="*", bd=2)
    password_entry.pack(pady=5)

    login_button = create_rounded_button(login_frame, "Login", lambda: login_callback(username_entry.get(), password_entry.get()))
    signup_button = create_rounded_button(login_frame, "Sign Up", signup_callback)

    return login_frame

# Call GUI with contacts and call options
def create_call_gui(root, username, contact_list, start_call_callback, end_call_callback, mute_callback):
    call_frame = tk.Frame(root, bg="#f0f0f0")
    call_frame.pack(fill="both", expand=True)

    title = tk.Label(call_frame, text=f"Welcome {username}", font=("Arial", 24), bg="#f0f0f0", fg="#4b0079")
    title.pack(pady=30)

    contact_label = tk.Label(call_frame, text="Contacts", font=("Arial", 18), bg="#f0f0f0", fg="#4b0079")
    contact_label.pack()

    contact_listbox = tk.Listbox(call_frame, font=("Arial", 14), height=6, width=40, bd=2, relief="flat")
    contact_listbox.pack(pady=10)

    # Load contacts dynamically
    for contact in contact_list:
        contact_listbox.insert(tk.END, contact)

    connect_button = create_rounded_button(call_frame, "Connect", lambda: start_call_callback(contact_listbox.get(contact_listbox.curselection())))

    call_controls_frame = tk.Frame(call_frame, bg="#f0f0f0")
    call_controls_frame.pack(pady=20)

    end_call_button = create_rounded_button(call_controls_frame, "End Call", end_call_callback)
    mute_button = create_rounded_button(call_controls_frame, "Mute", mute_callback)

    return call_frame

# Main application
class VOIPClient:
    def __init__(self, root):
        self.root = root
        self.root.title("VOIP Client")
        self.root.geometry("600x600")

        # Set up initial UI state
        self.username = None
        self.contact_list = []  # Example: ["John", "Jane", "Alice"]
        self.is_connected = False

        self.login_frame = create_login_gui(self.root, self.login, self.signup)

    def login(self, username, password):
        if username and password:
            # Simulate user authentication
            self.username = username
            self.contact_list = ["John", "Jane", "Alice"]  # Example contacts, this would come from the DB
            self.create_call_gui()
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")

    def signup(self):
        def submit_signup():
            username = signup_username.get()
            password = signup_password.get()
            if username and password:
                # Simulate user registration (you can replace with actual DB logic)
                messagebox.showinfo("Success", "User registered successfully!")
                signup_window.destroy()
            else:
                messagebox.showerror("Error", "Please fill in both fields.")

        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")
        signup_window.geometry("400x300")

        signup_username = tk.Entry(signup_window, font=("Arial", 14))
        signup_username.pack(pady=10)
        signup_password = tk.Entry(signup_window, font=("Arial", 14), show="*")
        signup_password.pack(pady=10)

        signup_button = tk.Button(signup_window, text="Register", font=("Arial", 14), command=submit_signup)
        signup_button.pack(pady=20)

    def create_call_gui(self):
        if self.login_frame:
            self.login_frame.destroy()

        self.call_frame = create_call_gui(self.root, self.username, self.contact_list, self.start_call, self.end_call, self.mute)

    def start_call(self, contact):
        if not self.is_connected:
            messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        messagebox.showinfo("Calling", f"Calling {contact}...")
        # Add actual call logic (audio streaming via sockets, etc.)
        self.is_connected = True

    def end_call(self):
        self.is_connected = False
        messagebox.showinfo("Call Ended", "The call has been ended.")

    def mute(self):
        if self.is_connected:
            messagebox.showinfo("Mute", "The call has been muted.")
        else:
            messagebox.showwarning("No Call", "No call is in progress to mute.")

# Running the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VOIPClient(root)
    root.mainloop()
