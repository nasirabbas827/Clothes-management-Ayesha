import tkinter as tk
from tkinter import messagebox, ttk
from admin_dashboard import AdminDashboard
from user_dashboard import UserDashboard
from database import authenticate_user

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("System Login - Clothes Management")
        self.root.state('zoomed')
        self.root.configure(bg="#f5f7f9") # Soft light grey/blue background

        self.build_ui()

    def build_ui(self):
        # Main container with a gradient-like background color
        main_frame = tk.Frame(self.root, bg="#f5f7f9")
        main_frame.pack(fill="both", expand=True)

        # White Card for the Login Form
        card = tk.Frame(main_frame, bg="#ffffff", padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Simulated Shadow/Border
        card.configure(highlightbackground="#e0e0e0", highlightthickness=1)

        # Header Section
        tk.Label(
            card, text="Welcome Back", 
            font=("Helvetica", 24, "bold"), 
            bg="#ffffff", fg="#2d3436"
        ).pack(pady=(0, 5))

        tk.Label(
            card, text="Login to manage your inventory", 
            font=("Helvetica", 11), 
            bg="#ffffff", fg="#636e72"
        ).pack(pady=(0, 30))

        # Input Style Configuration
        input_style = {"font": ("Helvetica", 12), "bg": "#f1f3f5", "fg": "#2d3436", 
                       "relief": "flat", "insertbackground": "#3498db"}

        # Username
        self.create_label(card, "USERNAME")
        self.username = tk.Entry(card, **input_style)
        self.username.pack(fill="x", ipady=12, pady=(0, 20))
        self.username.insert(0, "Enter your username")
        self.username.bind("<FocusIn>", lambda e: self.on_entry_click(self.username, "Enter your username"))

        # Password
        self.create_label(card, "PASSWORD")
        self.password = tk.Entry(card, show="*", **input_style)
        self.password.pack(fill="x", ipady=12, pady=(0, 20))

        # Role Selection (Styled Combobox)
        self.create_label(card, "SELECT ROLE")
        self.role_var = tk.StringVar()
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#f1f3f5", background="#f1f3f5", 
                        borderwidth=0, arrowsize=15)
        
        self.role_dropdown = ttk.Combobox(card, textvariable=self.role_var, state='readonly', 
                                          font=("Helvetica", 12), style="TCombobox")
        self.role_dropdown['values'] = ("Admin", "User")
        self.role_dropdown.current(0)
        self.role_dropdown.pack(fill="x", ipady=8, pady=(0, 30))

        # Login Button
        self.login_btn = tk.Button(
            card, text="SIGN IN", 
            command=self.login, 
            font=("Helvetica", 12, "bold"), 
            bg="#3498db", fg="white", 
            activebackground="#2980b9", activeforeground="white",
            bd=0, cursor="hand2"
        )
        self.login_btn.pack(fill="x", ipady=12)

        

    def create_label(self, parent, text):
        """Helper to create consistent small uppercase labels"""
        lbl = tk.Label(parent, text=text, font=("Helvetica", 8, "bold"), 
                       bg="#ffffff", fg="#b2bec3")
        lbl.pack(anchor="w", pady=(0, 5))

    def on_entry_click(self, entry, placeholder):
        """Clears placeholder text on click"""
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg="#2d3436")

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        role = self.role_var.get()

        # Simple validation before database call
        if user == "" or user == "Enter your username" or pwd == "":
            messagebox.showwarning("Input Error", "Please fill in all fields")
            return

        user_data = authenticate_user(user, pwd, role)
        if user_data:
            self.root.destroy()
            new_root = tk.Tk()
            if role == "Admin":
                AdminDashboard(new_root, {'username': user, 'role': role})
            else:
                UserDashboard(new_root, {'username': user, 'role': role})
            new_root.mainloop()
        else:
            messagebox.showerror("Access Denied", "Invalid username or password.")

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()