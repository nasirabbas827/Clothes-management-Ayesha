import tkinter as tk
from tkinter import messagebox
from user_items import UserItemsWindow

class UserDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title("Clothes Management | Staff Dashboard")
        self.root.state('zoomed')
        self.root.configure(bg="#f8f9fa")

        # Color Palette
        self.colors = {
            "primary": "#2c3e50",
            "accent": "#3498db",
            "danger": "#e74c3c",
            "white": "#ffffff"
        }

        self.setup_ui()

    def setup_ui(self):
        # --- Top Navigation Bar ---
        nav_bar = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        nav_bar.pack(fill=tk.X)
        
        tk.Label(nav_bar, text="Clothes Management Terminal", font=("Helvetica", 18, "bold"), 
                 fg="white", bg=self.colors["primary"]).pack(side=tk.LEFT, padx=30, pady=15)
        
        # Logout on the right
        tk.Button(nav_bar, text="LOGOUT", font=("Arial", 9, "bold"), bg=self.colors["danger"], 
                  fg="white", padx=20, pady=8, relief="flat", cursor="hand2", 
                  command=self.logout).pack(side=tk.RIGHT, padx=30)

        # --- Central Action Area ---
        center_frame = tk.Frame(self.root, bg="#f8f9fa")
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Welcome Text
        username = self.user_data.get('username', 'User').capitalize()
        tk.Label(center_frame, text=f"Welcome back, {username}", font=("Helvetica", 24, "bold"), 
                 bg="#f8f9fa", fg=self.colors["primary"]).pack(pady=(0, 10))
        
        tk.Label(center_frame, text="Ready to process new transactions?", font=("Arial", 12), 
                 bg="#f8f9fa", fg="#7f8c8d").pack(pady=(0, 40))

        # Big Action Button for Sales
        sale_btn = tk.Button(center_frame, text="🛒  OPEN SALES TERMINAL", 
                             font=("Helvetica", 14, "bold"), bg=self.colors["accent"], 
                             fg="white", width=30, pady=20, relief="flat", 
                             cursor="hand2", command=self.open_items_window)
        sale_btn.pack()

        # Simple Info Footer
        tk.Label(self.root, text="System Mode: Sales Only", font=("Arial", 9), 
                 bg="#f8f9fa", fg="#bdc3c7").pack(side=tk.BOTTOM, pady=20)

    def open_items_window(self):
        """Opens the sales and items view."""
        self.root.withdraw()
        items_window = tk.Toplevel()
        UserItemsWindow(items_window, self.user_data, self.root)

    def logout(self):
        """Returns to the login screen."""
        if messagebox.askyesno("Logout", "Are you sure you want to exit your session?"):
            self.root.destroy()
            import login
            root = tk.Tk()
            login.LoginWindow(root)
            root.mainloop()