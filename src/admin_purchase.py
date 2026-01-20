import tkinter as tk
from tkinter import ttk, messagebox
import database 
from PIL import Image, ImageTk
import os
from datetime import datetime

class AdminPurchaseWindow:
    def __init__(self, root, user_data, parent_root):
        self.root = root
        self.user_data = user_data
        self.parent_root = parent_root
        self.root.title("Clothes Management | Automated Purchase Entry")
        self.root.state("zoomed")
        self.root.configure(bg="#89baec")

        self.colors = {
            "primary": "#2c3e50", "accent": "#3498db",
            "success": "#27ae60", "bg": "#89baec", "white": "#89baec"
        }

        self.item_list = []
        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="Inventory Purchase Management", font=("Helvetica", 16, "bold"), 
                 fg="white", bg=self.colors["primary"]).pack(side=tk.LEFT, padx=25, pady=12)

        # Main Content
        main_content = tk.Frame(self.root, bg=self.colors["bg"])
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # LEFT PANEL: Table
        left_panel = tk.Frame(main_content, bg="white")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Search Records
        search_area = tk.Frame(left_panel, bg="#ecf0f1", pady=10)
        search_area.pack(fill=tk.X)
        tk.Label(search_area, text="Filter Records:", font=("Segoe UI", 10, "bold"), bg="#ecf0f1").pack(side=tk.LEFT, padx=(15, 5))
        self.record_search_var = tk.StringVar()
        search_ent = tk.Entry(search_area, textvariable=self.record_search_var, font=("Segoe UI", 10))
        search_ent.pack(side=tk.LEFT, padx=5)
        search_ent.bind("<KeyRelease>", lambda e: self.filter_data())

        # Table Columns (Total is calculated: Qty * Item Cost)
        cols = ("purchase_id", "item_name", "category", "qty", "unit_cost", "total", "date")
        self.purchase_tree = ttk.Treeview(left_panel, columns=cols, show='headings')
        
        headings = ["Purchase ID", "Item Name", "Category", "Qty Purchased", "Unit Cost", "Total Amount", "Date"]
        for i, col in enumerate(cols):
            self.purchase_tree.heading(col, text=headings[i])
            self.purchase_tree.column(col, anchor="center", width=100)

        self.purchase_tree.pack(fill=tk.BOTH, expand=True)

        # RIGHT PANEL: Form
        right_container = tk.Frame(main_content, bg="white", width=380)
        right_container.pack(side=tk.RIGHT, fill=tk.Y)
        right_container.pack_propagate(False)

        self.form_frame = tk.Frame(right_container, bg="white", padx=20)
        self.form_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_form()
        self.load_items_into_dropdown()
        self.load_purchase_history()

    def setup_form(self):
        tk.Label(self.form_frame, text="RECORD STOCK ENTRY", font=("Helvetica", 13, "bold"), 
                 bg="white", fg=self.colors["primary"]).pack(pady=30)

        # Item Selection
        tk.Label(self.form_frame, text="SEARCH & SELECT ITEM", font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w", padx=10)
        self.item_selector = ttk.Combobox(self.form_frame, font=("Segoe UI", 11), state="normal")
        self.item_selector.pack(fill="x", padx=10, pady=(2, 20))
        self.item_selector.bind("<KeyRelease>", self.on_dropdown_filter)

        # Quantity Input
        tk.Label(self.form_frame, text="QUANTITY TO ADD", font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack(anchor="w", padx=10)
        self.qty_ent = tk.Entry(self.form_frame, font=("Segoe UI", 12), bg="#f8f9fa", relief="flat", highlightthickness=1)
        self.qty_ent.pack(fill="x", padx=10, pady=(2, 20))

        # Note about Automation
        tk.Label(self.form_frame, text="* Cost is calculated automatically from Item Master", 
                 font=("Segoe UI", 8, "italic"), bg="white", fg="#e67e22").pack(pady=5)

        # Action Buttons
        tk.Button(self.form_frame, text="CONFIRM PURCHASE", command=self.submit_purchase, 
                  bg=self.colors["success"], fg="white", font=("Segoe UI", 11, "bold"), 
                  relief="flat", pady=12).pack(fill="x", padx=10, pady=20)

        tk.Button(self.form_frame, text="BACK TO DASHBOARD", command=self.on_close, 
                  bg="#95a5a6", fg="white", font=("Segoe UI", 10, "bold"), 
                  relief="flat", pady=8).pack(fill="x", padx=10, pady=5)

    def load_items_into_dropdown(self):
        conn = database.get_db_connection()
        items = conn.execute("SELECT item_id, name, category FROM cloth_items").fetchall()
        conn.close()
        self.item_list = [f"{i['name']} (ID:{i['item_id']}) | {i['category']}" for i in items]
        self.item_selector['values'] = self.item_list

    def on_dropdown_filter(self, event):
        value = event.widget.get().lower()
        if value == '':
            event.widget['values'] = self.item_list
        else:
            data = [item for item in self.item_list if value in item.lower()]
            event.widget['values'] = data

    def load_purchase_history(self, search_term=""):
        for i in self.purchase_tree.get_children(): self.purchase_tree.delete(i)
        
        conn = database.get_db_connection()
        # Formula: Pull cost_price from cloth_items and calculate total dynamically
        query = """
            SELECT p.purchase_id, i.name, i.category, p.quantity_purchased, i.cost_price,
                   (p.quantity_purchased * i.cost_price) as total_amt, p.purchase_date 
            FROM purchases p
            JOIN cloth_items i ON p.item_id = i.item_id
        """
        if search_term:
            query += f" WHERE i.name LIKE '%{search_term}%' OR i.category LIKE '%{search_term}%'"
        
        query += " ORDER BY p.purchase_id DESC"
        
        records = conn.execute(query).fetchall()
        conn.close()
        
        for r in records:
            self.purchase_tree.insert('', tk.END, values=(
                r[0], r[1], r[2], r[3], f"RS {r[4]:.2f}", f"RS {r[5]:.2f}", r[6]
            ))

    def filter_data(self):
        self.load_purchase_history(self.record_search_var.get())

    def submit_purchase(self):
        try:
            selected_str = self.item_selector.get()
            if "ID:" not in selected_str:
                raise ValueError("Please select a valid item from the list.")
            
            item_id = int(selected_str.split("ID:")[1].split(")")[0])
            qty = int(self.qty_ent.get())

            # Calls the automated function in database.py (no cost passed)
            database.record_purchase(item_id, qty)
            
            messagebox.showinfo("Success", f"Added {qty} units to inventory!")
            self.qty_ent.delete(0, tk.END)
            self.item_selector.set('')
            self.load_purchase_history()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid numeric quantity.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record: {e}")

    def on_close(self):
        self.root.destroy()
        self.parent_root.deiconify()