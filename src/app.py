import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from login import LoginWindow
import os

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title(" Clothes Management System")

        # Maximize window
        self.root.state('zoomed')
        self.root.resizable(True, True)
        self.root.configure(bg="#f8f9fa") # Clean white background

        self.build_ui()

    def build_ui(self):
        # Main container
        self.splash_frame = tk.Frame(self.root, bg="#ffffff")
        self.splash_frame.pack(fill="both", expand=True)

        # Center content frame
        splash_inner = tk.Frame(self.splash_frame, bg="#ffffff", padx=20, pady=20)
        splash_inner.place(relx=0.5, rely=0.5, anchor="center")

        # Title - Using a modern Navy/Charcoal color
        tk.Label(
            splash_inner,
            text="CLOTHES MANAGEMENT SYSTEM",
            font=("Helvetica", 28, "bold"),
            fg="#2c3e50",
            bg="#ffffff"
        ).pack(pady=(20, 5))

        # Tagline - Specific to Apparel/Fashion Management
        tk.Label(
            splash_inner,
            text="Organize Your Inventory with Style",
            font=("Helvetica", 14, "italic"),
            fg="#7f8c8d",
            bg="#ffffff"
        ).pack(pady=(0, 30))

        # Logo image handling
        logo_path = os.path.join("logos", "logo.png")
        if os.path.exists(logo_path):
            try:
                self.logo_img = PhotoImage(file=logo_path)
                tk.Label(splash_inner, image=self.logo_img, bg="#ffffff").pack(pady=10)
            except Exception:
                self.show_placeholder_logo(splash_inner)
        else:
            self.show_placeholder_logo(splash_inner)

        # Loading section
        tk.Label(
            splash_inner,
            text="Initializing Wardrobe Database...",
            font=("Segoe UI", 10),
            fg="#95a5a6",
            bg="#ffffff"
        ).pack(pady=(30, 5))

        # Modern styled progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", thickness=10, troughcolor='#ecf0f1', background='#3498db')
        
        self.progress = ttk.Progressbar(splash_inner, mode="indeterminate", length=400, style="TProgressbar")
        self.progress.pack(pady=10)
        self.progress.start(15)

        # Redirect to login after 3 seconds
        self.root.after(3000, self.redirect_to_login)

    def show_placeholder_logo(self, parent):
        """Helper to show a placeholder if the image is missing."""
        logo_frame = tk.Frame(parent, width=120, height=120, bg="#f8f9fa", relief="flat", highlightbackground="#dee2e6", highlightthickness=1)
        logo_frame.pack(pady=10)
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="👗", font=("Arial", 40), bg="#f8f9fa").place(relx=0.5, rely=0.5, anchor="center")

    def redirect_to_login(self):
        self.progress.stop()
        # Clear the splash screen widgets instead of destroying root
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Initialize Login Window in the same root
        LoginWindow(self.root)

if __name__ == '__main__':
    root = tk.Tk()
    app = SplashScreen(root)
    root.mainloop()