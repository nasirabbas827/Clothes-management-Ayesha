import tkinter as tk
from tkinter import messagebox, ttk
import database

def open_manage_users():
    root = tk.Tk()
    ManageUsers(root)
    root.mainloop()

class ManageUsers:
    def __init__(self, root):
        self.root = root
        self.root.title("Clothes Management | Manage System Users")
        self.root.state("zoomed")
        self.root.configure(bg="#f5f7f9")

        self.colors = {
            "primary": "#2c3e50",
            "info": "#2196F3",
            "success": "#4CAF50",
            "danger": "#f44336",
            "bg": "#f5f7f9",
            "white": "#ffffff",
            "text": "#333333"
        }

        self.build_ui()

    def build_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Header Section
        header_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            header_frame, text="User Management", 
            font=("Helvetica", 24, "bold"), fg=self.colors["primary"], bg=self.colors["bg"]
        ).pack(side="left")

        # Layout: Left (Table) and Right (Form)
        content_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # --- LEFT PANEL: Table ---
        left_panel = tk.Frame(content_frame, bg=self.colors["white"], padx=15, pady=15)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        left_panel.configure(highlightbackground="#e0e0e0", highlightthickness=1)

        tk.Label(left_panel, text="Access Directory", font=("Helvetica", 12, "bold"), 
                 bg=self.colors["white"], fg="#7f8c8d").pack(anchor="w", pady=(0, 15))

        # Modern Treeview Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Helvetica", 11), rowheight=35, borderwidth=0)
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), background="#f1f3f5", relief="flat")
        style.map("Treeview", background=[('selected', '#e3f2fd')], foreground=[('selected', '#2196F3')])

        columns = ("user_id", "username", "role")
        self.user_tree = ttk.Treeview(left_panel, columns=columns, show="headings", selectmode="browse")
        self.user_tree.heading("user_id", text="ID")
        self.user_tree.heading("username", text="USERNAME")
        self.user_tree.heading("role", text="ROLE")

        self.user_tree.column("user_id", width=50, anchor=tk.CENTER)
        self.user_tree.column("username", width=250)
        self.user_tree.column("role", width=120, anchor=tk.CENTER)

        self.user_tree.pack(fill=tk.BOTH, expand=True)
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)

        # --- RIGHT PANEL: Form ---
        right_panel = tk.Frame(content_frame, bg=self.colors["white"], padx=25, pady=25, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        right_panel.configure(highlightbackground="#e0e0e0", highlightthickness=1)

        tk.Label(right_panel, text="User Details", font=("Helvetica", 14, "bold"), 
                 bg=self.colors["white"], fg=self.colors["primary"]).pack(pady=(0, 20))

        # Input Helper
        def create_input(label_text):
            tk.Label(right_panel, text=label_text, font=("Helvetica", 9, "bold"), 
                     bg=self.colors["white"], fg="#b2bec3").pack(anchor="w", pady=(10, 2))
            entry = tk.Entry(right_panel, font=("Helvetica", 12), bg="#f1f3f5", relief="flat", bd=0)
            entry.pack(fill="x", ipady=8)
            return entry

        self.username_entry = create_input("USERNAME")
        self.password_entry = create_input("PASSWORD")
        self.password_entry.config(show="*")

        tk.Label(right_panel, text="ROLE", font=("Helvetica", 9, "bold"), 
                 bg=self.colors["white"], fg="#b2bec3").pack(anchor="w", pady=(10, 2))
        self.role_var = tk.StringVar()
        self.role_combobox = ttk.Combobox(right_panel, textvariable=self.role_var, values=["Admin", "User"], 
                                          state="readonly", font=("Helvetica", 11))
        self.role_combobox.pack(fill="x", ipady=5)

        # Action Buttons
        btn_container = tk.Frame(right_panel, bg=self.colors["white"])
        btn_container.pack(fill="x", pady=30)

        # EXACT BUTTONS AS REQUESTED
        self.add_button = tk.Button(btn_container, text="Add User", width=15, font=("Arial", 12, "bold"), 
                                    bg="#2196F3", fg="white", bd=0, relief="flat", command=self.add_user)
        self.add_button.grid(row=0, column=0, pady=5, padx=2)

        self.update_button = tk.Button(btn_container, text="Update User", width=15, font=("Arial", 12, "bold"), 
                                       bg="#4CAF50", fg="white", bd=0, relief="flat", command=self.update_user, state=tk.DISABLED)
        self.update_button.grid(row=0, column=1, pady=5, padx=2)

        tk.Button(right_panel, text="Delete User", width=32, font=("Arial", 12, "bold"), 
                  bg="#f44336", fg="white", bd=0, relief="flat", command=self.delete_user).pack(pady=5)

        tk.Button(right_panel, text="Back to Dashboard", width=32, font=("Arial", 12, "bold"), 
                  bg="#4CAF50", fg="white", bd=0, relief="flat", command=self.go_back).pack(pady=20)

        self.selected_user_id = None
        self.load_users()

    # --- Logic Methods (Kept from your original) ---

    def load_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, role FROM users")
        users = cursor.fetchall()
        conn.close()
        for user in users:
            self.user_tree.insert("", tk.END, values=(user['user_id'], user['username'], user['role']))
        self.clear_form()

    def on_user_select(self, event):
        selected = self.user_tree.selection()
        if not selected: return
        user_id = self.user_tree.item(selected[0])['values'][0]
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.selected_user_id = user['user_id']
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, user['username'])
            self.password_entry.delete(0, tk.END)
            self.role_combobox.set(user['role'])
            self.update_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.DISABLED)

    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        if not username or not password or not role:
            messagebox.showerror("Error", "All fields are required")
            return
        try:
            database.add_user(username, password, role)
            messagebox.showinfo("Success", "User added!")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        try:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            if password:
                cursor.execute("UPDATE users SET username=?, password=?, role=? WHERE user_id=?", 
                               (username, password, role, self.selected_user_id))
            else:
                cursor.execute("UPDATE users SET username=?, role=? WHERE user_id=?", 
                               (username, role, self.selected_user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User updated!")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected: return
        user_id = self.user_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete this user?"):
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            self.load_users()

    def clear_form(self):
        self.selected_user_id = None
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_combobox.set("")
        self.update_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)

    def go_back(self):
        self.root.destroy()
        from admin_dashboard import AdminDashboard
        root = tk.Tk()
        AdminDashboard(root, {'username': 'admin', 'role': 'Admin'})
        root.mainloop()