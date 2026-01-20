import tkinter as tk
from tkinter import ttk, messagebox
from reports import ReportsWindow
from database import get_db_connection
from admin_purchase import AdminPurchaseWindow  

class AdminDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title("Executive Admin Panel")
        self.root.state("zoomed")
        self.root.configure(bg="#f4f7f6")
        
        # Color Palette
        self.colors = {
            "primary": "#2c3e50",    # Dark Navy
            "accent": "#3498db",     # Bright Blue
            "success": "#27ae60",    # Green for Profit
            "warning": "#f39c12",    # Orange
            "danger": "#e74c3c",     # Red
            "bg_light": "#f4f7f6",   # Light Grey
            "white": "#ffffff",
            "text": "#34495e"
        }

        self.build_ui()

    def fetch_metrics(self):
        """Fetches live business data from database.py logic."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 1. Total Revenue (Sales)
            cursor.execute('SELECT SUM(quantity_sold * sale_price) FROM sales')
            revenue = cursor.fetchone()[0] or 0.0

            # 2. Total Expenditure (Stock Investment)
            cursor.execute('SELECT SUM(p.quantity_purchased * i.cost_price) FROM purchases p JOIN cloth_items i ON p.item_id = i.item_id')
            investment = cursor.fetchone()[0] or 0.0

            # 3. Net Profit (Revenue - Cost of Items Sold)
            cursor.execute('''
                SELECT SUM(s.quantity_sold * (s.sale_price - i.cost_price)) 
                FROM sales s JOIN cloth_items i ON s.item_id = i.item_id
            ''')
            net_profit = cursor.fetchone()[0] or 0.0

            # 4. Total Inventory Count
            cursor.execute('SELECT SUM(stock_quantity) FROM cloth_items')
            total_stock = cursor.fetchone()[0] or 0

            conn.close()
            return revenue, investment, net_profit, total_stock
        except Exception as e:
            print(f"Metrics Error: {e}")
            return 0.0, 0.0, 0.0, 0

    def build_ui(self):
        # --- Sidebar Navigation ---
        sidebar = tk.Frame(self.root, bg=self.colors["primary"], width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Clothes Management", font=("Helvetica", 22, "bold"), 
                 bg=self.colors["primary"], fg="white", pady=40).pack()

        nav_items = [
            ("👥 Manage Users", self.open_manage_users),
            ("👕 Cloth Inventory", self.open_manage_items),
            ("🛒 Stock Purchase", self.open_user_purchase),
            ("📊 Sales Reports", self.open_reports_window),
            ("🔄 Refresh Stats", self.refresh_dashboard),
            ("🚪 Logout", self.logout)
        ]

        for text, cmd in nav_items:
            btn = tk.Button(sidebar, text=text, font=("Arial", 11), bg=self.colors["primary"],
                            fg="white", bd=0, padx=25, pady=15, anchor="w", 
                            activebackground="#34495e", activeforeground="white", 
                            cursor="hand2", command=cmd)
            btn.pack(fill="x")

        # --- Main Workspace ---
        self.content = tk.Frame(self.root, bg=self.colors["bg_light"], padx=40, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # Header
        header = tk.Frame(self.content, bg=self.colors["bg_light"])
        header.pack(fill="x", pady=(0, 30))
        
        tk.Label(header, text="Business Overview", font=("Helvetica", 26, "bold"), 
                 bg=self.colors["bg_light"], fg=self.colors["primary"]).pack(side="left")
        
        tk.Label(header, text=f"Logged in as: {self.user_data['username'].upper()}", 
                 font=("Arial", 10, "italic"), bg=self.colors["bg_light"], fg="#95a5a6").pack(side="right", pady=15)

        self.render_metrics()

    def render_metrics(self):
        """Builds the 4-card metric display."""
        # Container for cards
        metrics_frame = tk.Frame(self.content, bg=self.colors["bg_light"])
        metrics_frame.pack(fill="x")

        rev, inv, profit, stock = self.fetch_metrics()

        cards = [
            ("TOTAL REVENUE", f"Rs {rev:,.2f}", self.colors["accent"]),
            ("STOCK INVESTMENT", f"Rs {inv:,.2f}", self.colors["warning"]),
            ("NET PROFIT", f"Rs {profit:,.2f}", self.colors["success"]),
            ("TOTAL STOCK", f"{stock:,} Pcs", self.colors["primary"]),
        ]

        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(metrics_frame, bg="white", padx=20, pady=25, 
                            highlightthickness=1, highlightbackground="#e0e0e0")
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            
            tk.Label(card, text=title, font=("Arial", 9, "bold"), bg="white", fg="#bdc3c7").pack(anchor="w")
            tk.Label(card, text=value, font=("Helvetica", 18, "bold"), bg="white", fg=color).pack(anchor="w", pady=(10, 0))
        
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1)

    def refresh_dashboard(self):
        """Clears and re-renders metrics to show latest data."""
        for widget in self.content.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_y() > 50: # Keep the header
                widget.destroy()
        self.render_metrics()
        messagebox.showinfo("Update", "Metrics updated successfully!")

    def open_manage_users(self):
        self.root.destroy()
        import manage_users
        manage_users.open_manage_users()

    def open_manage_items(self):
        self.root.destroy()
        import manage_items
        manage_items.open_manage_items()

    def open_user_purchase(self):
        self.root.withdraw()
        purchase_root = tk.Toplevel()
        AdminPurchaseWindow(purchase_root, self.user_data, self.root)

    def open_reports_window(self):
        self.root.withdraw()
        reports_window = tk.Toplevel()
        ReportsWindow(reports_window, self.user_data, self.root)

    def logout(self):
        self.root.destroy()
        import login
        root = tk.Tk()
        login.LoginWindow(root)
        root.mainloop()