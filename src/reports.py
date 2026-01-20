import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from tkcalendar import DateEntry
from database import generate_report

class ReportsWindow:
    def __init__(self, root, user_data, parent_root):
        self.root = root
        self.user_data = user_data
        self.parent_root = parent_root
        self.root.title("Analytics & Reports")
        self.root.state("zoomed")
        self.root.configure(bg="#f0f2f5")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Theme Colors
        self.colors = {
            "primary": "#2c3e50",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "white": "#ffffff",
            "bg": "#f0f2f5"
        }

        self.build_ui()

    def build_ui(self):
        # --- Header ---
        header = tk.Frame(self.root, bg=self.colors["primary"], height=70)
        header.pack(fill=tk.X)
        tk.Label(header, text="Business Intelligence & Reports", font=("Helvetica", 18, "bold"), 
                 fg="white", bg=self.colors["primary"]).pack(side=tk.LEFT, padx=30, pady=15)

        # --- Main Container ---
        main_content = tk.Frame(self.root, bg=self.colors["bg"])
        main_content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        # --- Top Section: Report Options ---
        selection_frame = tk.Frame(main_content, bg="white", relief="flat", padx=20, pady=20)
        selection_frame.pack(fill=tk.X, pady=(0, 20))

        # Row 1: Report Type & Dates
        tk.Label(selection_frame, text="Report Type:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=0, column=0, sticky="w", padx=5)
        self.report_type_var = tk.StringVar(value="stock")
        report_dropdown = ttk.Combobox(selection_frame, textvariable=self.report_type_var, 
                                       values=["stock", "sales", "purchases", "profit"], state="readonly", width=15, font=("Segoe UI", 10))
        report_dropdown.grid(row=0, column=1, padx=10)

        # Date Range Frame (Dynamically toggled)
        self.date_frame = tk.Frame(selection_frame, bg="white")
        self.date_frame.grid(row=0, column=2, padx=20)

        tk.Label(self.date_frame, text="From:", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(self.date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.pack(side=tk.LEFT, padx=5)

        tk.Label(self.date_frame, text="To:", font=("Segoe UI", 10), bg="white").pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(self.date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.pack(side=tk.LEFT, padx=5)

        # Row 2: Actions (All buttons on the same line)
        btn_container = tk.Frame(selection_frame, bg="white")
        btn_container.grid(row=1, column=0, columnspan=3, sticky="w", pady=(20, 0))

        tk.Button(btn_container, text="Generate View", command=self.generate_report, 
                  bg=self.colors["accent"], fg="white", font=("Segoe UI", 10, "bold"), 
                  relief="flat", padx=20, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_container, text="Export as CSV", command=self.export_report, 
                  bg=self.colors["success"], fg="white", font=("Segoe UI", 10, "bold"), 
                  relief="flat", padx=20, pady=8).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_container, text="Back to Dashboard", command=self.on_close, 
                  bg=self.colors["danger"], fg="white", font=("Segoe UI", 10, "bold"), 
                  relief="flat", padx=20, pady=8).pack(side=tk.LEFT, padx=5)

        # --- Bottom Section: Output Table ---
        table_frame = tk.Frame(main_content, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Styling the Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.tree = ttk.Treeview(table_frame, show="headings")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initial visibility setup
        self.report_type_var.trace('w', self.toggle_date_frame)
        self.toggle_date_frame()

    def toggle_date_frame(self, *args):
        if self.report_type_var.get() == "stock":
            self.date_frame.grid_remove()
        else:
            self.date_frame.grid()

    def generate_report(self):
        report_type = self.report_type_var.get()
        self.tree.delete(*self.tree.get_children())
        
        start_date = self.start_date.get() if report_type != "stock" else None
        end_date = self.end_date.get() if report_type != "stock" else None

        report_data = generate_report(report_type, start_date, end_date)

        if not report_data:
            messagebox.showinfo("Info", "No records found for this period.")
            return

        if report_type == "stock":
            self.setup_table(("ID", "Item Name", "Category", "Qty In Stock"), report_data, 
                             lambda x: (x['item_id'], x['name'], x['category'], x['stock_quantity']))

        elif report_type == "sales":
            self.setup_table(("Sale ID", "Name", "Qty Sold", "Price", "Date"), report_data,
                             lambda x: (x['sale_id'], x['name'], x['quantity_sold'], f"RS {x['sale_price']}", x['sale_date']))

        elif report_type == "purchases":
            self.setup_table(("Purchase ID", "Name", "Qty Bought", "Cost", "Date"), report_data,
                             lambda x: (x['purchase_id'], x['name'], x['quantity_purchased'], f"RS {x['cost_price']}", x['purchase_date']))

        elif report_type == "profit":
            self.setup_table(("Metric", "Amount"), [], None)
            self.tree.insert('', tk.END, values=("Sales Revenue", f"RS {report_data['sales_profit']:.2f}"))
            self.tree.insert('', tk.END, values=("Purchase Expenditure", f"RS {report_data['purchase_profit']:.2f}"))
            total = report_data['total_profit']
            self.tree.insert('', tk.END, values=("NET PROFIT", f"RS {total:.2f}"))

    def setup_table(self, columns, data, mapping_func):
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=180)
        
        if mapping_func:
            for item in data:
                self.tree.insert('', tk.END, values=mapping_func(item))

    def export_report(self):
        report_type = self.report_type_var.get()
        report_data = generate_report(report_type, self.start_date.get(), self.end_date.get())
        
        if not report_data:
            messagebox.showerror("Error", "Nothing to export.")
            return

        os.makedirs("exports", exist_ok=True)
        filename = f"exports/{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                if report_type == "stock":
                    writer.writerow(["ID", "Name", "Category", "Stock"])
                    [writer.writerow([i['item_id'], i['name'], i['category'], i['stock_quantity']]) for i in report_data]
                elif report_type == "sales":
                    writer.writerow(["Sale ID", "Name", "Qty", "Price", "Date"])
                    [writer.writerow([s['sale_id'], s['name'], s['quantity_sold'], s['sale_price'], s['sale_date']]) for s in report_data]
                elif report_type == "purchases":
                    writer.writerow(["Purchase ID", "Name", "Qty", "Cost", "Date"])
                    [writer.writerow([p['purchase_id'], p['name'], p['quantity_purchased'], p['cost_price'], p['purchase_date']]) for p in report_data]
                elif report_type == "profit":
                    writer.writerow(["Metric", "Value"])
                    writer.writerow(["Sales Profit", report_data['sales_profit']])
                    writer.writerow(["Purchase Profit", report_data['purchase_profit']])
                    writer.writerow(["Total Profit", report_data['total_profit']])
            
            messagebox.showinfo("Success", f"Report saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def on_close(self):
        self.root.destroy()
        self.parent_root.deiconify()
        self.parent_root.state("zoomed")