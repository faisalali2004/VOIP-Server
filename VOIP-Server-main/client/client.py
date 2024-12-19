import tkinter as tk
from tkinter import messagebox
from database import init_db, register_user, authenticate_user, add_contact, remove_contact, get_contacts


# Helper function to create buttons
def create_button(parent, text, command, bg="#4b0079", fg="white"):
    button = tk.Button(parent, text=text, command=command, font=("Arial", 14), bg=bg, fg=fg)
    button.pack(pady=10)
    return button


# Login UI
def create_login_gui(root, login_callback, signup_callback):
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(fill="both", expand=True)

    title = tk.Label(frame, text="VOIP Login", font=("Arial", 24), bg="#f0f0f0", fg="#4b0079")
    title.pack(pady=20)

    username_label = tk.Label(frame, text="Username", font=("Arial", 16), bg="#f0f0f0", fg="#4b0079")
    username_label.pack()
    username_entry = tk.Entry(frame, font=("Arial", 14))
    username_entry.pack()

    password_label = tk.Label(frame, text="Password", font=("Arial", 16), bg="#f0f0f0", fg="#4b0079")
    password_label.pack()
    password_entry = tk.Entry(frame, font=("Arial", 14), show="*")
    password_entry.pack()

    login_button = create_button(frame, "Login", lambda: login_callback(username_entry.get(), password_entry.get()))
    signup_button = create_button(frame, "Sign Up", signup_callback)

    return frame


# Call Screen
def create_call_screen(root, contact, end_call_callback, mute_callback, unmute_callback):
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(fill="both", expand=True)

    title = tk.Label(frame, text=f"Calling {contact}...", font=("Arial", 24), bg="#f0f0f0", fg="#4b0079")
    title.pack(pady=20)

    mute_button = create_button(frame, "Mute", mute_callback, bg="#ffbf00", fg="black")
    unmute_button = create_button(frame, "Unmute", unmute_callback, bg="#ffbf00", fg="black")
    end_call_button = create_button(frame, "End Call", end_call_callback, bg="#e60000", fg="white")

    return frame


# Contact List UI
def create_contact_list_gui(root, username, contact_list, start_call_callback, add_contact_callback, remove_contact_callback):
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(fill="both", expand=True)

    title = tk.Label(frame, text=f"Welcome {username}", font=("Arial", 24), bg="#f0f0f0", fg="#4b0079")
    title.pack(pady=20)

    contact_label = tk.Label(frame, text="Contacts", font=("Arial", 18), bg="#f0f0f0", fg="#4b0079")
    contact_label.pack()

    for contact in contact_list:
        contact_frame = tk.Frame(frame, bg="#f0f0f0")
        contact_frame.pack(pady=5)

        create_button(contact_frame, contact, lambda contact=contact: start_call_callback(contact))
        create_button(contact_frame, f"Remove {contact}", lambda contact=contact: remove_contact_callback(contact))

    add_contact_button = create_button(frame, "Add Contact", add_contact_callback)

    return frame


# VOIP Client
class VOIPClient:
    def __init__(self, root):
        self.root = root
        self.root.title("VOIP Client")
        self.root.geometry("600x600")

        # Initialize database
        init_db()

        # Set up variables
        self.username = None
        self.user_id = None
        self.contact_list = []

        # Initialize UI
        self.current_frame = None
        self.show_login_screen()

    def show_login_screen(self):
        self.destroy_current_frame()
        self.current_frame = create_login_gui(self.root, self.login, self.signup)

    def show_contact_list_screen(self):
        self.destroy_current_frame()
        self.current_frame = create_contact_list_gui(self.root, self.username, self.contact_list, self.start_call, self.add_contact, self.remove_contact)

    def show_call_screen(self, contact):
        self.destroy_current_frame()
        self.current_frame = create_call_screen(self.root, contact, self.end_call, self.mute_call, self.unmute_call)

    def destroy_current_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def login(self, username, password):
        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in both fields.")
            return

        user = authenticate_user(username, password)
        if user:
            self.username = username
            self.user_id = user[0]  # Assuming user ID is the first field in the returned tuple
            self.contact_list = get_contacts(self.user_id)
            self.show_contact_list_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    def signup(self):
        def submit_signup():
            username = signup_username.get()
            password = signup_password.get()
            if username and password:
                if register_user(username, password):
                    messagebox.showinfo("Success", "User registered successfully!")
                    signup_window.destroy()
                    self.show_login_screen()
                else:
                    messagebox.showerror("Error", "User already exists.")
            else:
                messagebox.showwarning("Input Error", "Please fill in both fields.")

        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")
        signup_window.geometry("400x300")

        tk.Label(signup_window, text="Username:", font=("Arial", 14)).pack(pady=5)
        signup_username = tk.Entry(signup_window, font=("Arial", 14))
        signup_username.pack()

        tk.Label(signup_window, text="Password:", font=("Arial", 14)).pack(pady=5)
        signup_password = tk.Entry(signup_window, font=("Arial", 14), show="*")
        signup_password.pack()

        tk.Button(signup_window, text="Register", font=("Arial", 14), command=submit_signup).pack(pady=20)

    def start_call(self, contact):
        self.show_call_screen(contact)

    def end_call(self):
        messagebox.showinfo("Call Ended", "The call has ended.")
        self.show_contact_list_screen()

    def mute_call(self):
        messagebox.showinfo("Muted", "You have muted the call.")

    def unmute_call(self):
        messagebox.showinfo("Unmuted", "You have unmuted the call.")

    def add_contact(self):
        def submit_add_contact():
            contact_name = contact_name_entry.get()
            if contact_name:
                add_contact(self.user_id, contact_name)
                self.contact_list = get_contacts(self.user_id)
                add_contact_window.destroy()
                self.show_contact_list_screen()
            else:
                messagebox.showwarning("Input Error", "Please enter a valid contact name.")

        add_contact_window = tk.Toplevel(self.root)
        add_contact_window.title("Add Contact")
        add_contact_window.geometry("400x200")

        tk.Label(add_contact_window, text="Contact Name:", font=("Arial", 14)).pack(pady=5)
        contact_name_entry = tk.Entry(add_contact_window, font=("Arial", 14))
        contact_name_entry.pack(pady=10)

        tk.Button(add_contact_window, text="Add", font=("Arial", 14), command=submit_add_contact).pack(pady=10)

    def remove_contact(self, contact):
        remove_contact(self.user_id, contact)
        self.contact_list = get_contacts(self.user_id)
        messagebox.showinfo("Contact Removed", f"Contact {contact} has been removed.")
        self.show_contact_list_screen()


# Running the App
if __name__ == "__main__":
    root = tk.Tk()
    app = VOIPClient(root)
    root.mainloop()
