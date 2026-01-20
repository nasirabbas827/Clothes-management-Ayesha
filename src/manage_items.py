import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import os
from datetime import datetime
import database

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def open_manage_items():
    root = tk.Tk()
    ManageItems(root)
    root.mainloop()

class ManageItems:
    def __init__(self, root):
        self.root = root
        self.root.title("Clothes Management | Inventory Management System")
        self.root.state("zoomed")
        self.root.configure(bg="#f0f2f5")

        # UI Color Palette
        self.colors = {
            "primary": "#2c3e50",
            "accent": "#3498db",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "white": "#ffffff",
            "gray": "#7f8c8d"
        }

        self.selected_item_id = None
        self.image_path = None
        self.build_ui()

    def build_ui(self):
        # --- 1. SEARCH BAR (TOP) ---
        search_panel = tk.Frame(self.root, bg=self.colors["primary"], pady=10)
        search_panel.pack(fill=tk.X)

        tk.Label(search_panel, text="SEARCH BY:", font=("Arial", 9, "bold"), 
                 fg="white", bg=self.colors["primary"]).pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_by_var = tk.StringVar(value="name")
        search_options = ttk.Combobox(search_panel, textvariable=self.search_by_var, 
                                      values=["name", "item_id", "season", "size"], 
                                      state="readonly", width=12)
        search_options.pack(side=tk.LEFT, padx=5)

        self.search_ent = tk.Entry(search_panel, font=("Arial", 11), width=35)
        self.search_ent.pack(side=tk.LEFT, padx=5)
        self.search_ent.bind("<KeyRelease>", lambda e: self.perform_search())

        tk.Button(search_panel, text="RESET", command=self.load_items, 
                  bg=self.colors["gray"], fg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=10)

        # --- 2. MAIN CONTAINER ---
        main_content = tk.Frame(self.root, bg="#f0f2f5")
        main_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # LEFT PANEL: Treeview Table
        left_panel = tk.Frame(main_content, bg="white")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        cols = ("id", "name", "category", "price", "stock", "season", "size", "color")
        self.item_tree = ttk.Treeview(left_panel, columns=cols, show="headings")
        
        display_names = ["ID", "Name", "Category", "Price", "Stock", "Season", "Size", "Color"]
        for i, col in enumerate(cols):
            self.item_tree.heading(col, text=display_names[i])
            self.item_tree.column(col, width=90, anchor="center")

        tree_scrolly = ttk.Scrollbar(left_panel, orient="vertical", command=self.item_tree.yview)
        self.item_tree.configure(yscrollcommand=tree_scrolly.set)
        
        self.item_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # RIGHT PANEL: Scrollable Form
        right_container = tk.Frame(main_content, bg="white", width=400)
        right_container.pack(side=tk.RIGHT, fill=tk.Y)
        right_container.pack_propagate(False)

        # Canvas for Scrolling
        self.canvas = tk.Canvas(right_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=self.canvas.yview)
        self.form_frame = tk.Frame(self.canvas, bg="white")

        self.form_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw", width=380)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Bind Mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.setup_form()
        self.load_items()

    def setup_form(self):
        # Form Title
        tk.Label(self.form_frame, text="ITEM DETAILS", font=("Helvetica", 14, "bold"), 
                 bg="white", fg=self.colors["primary"]).pack(pady=15)

        self.entries = {}
        # Entry fields
        fields = [
            ("Item Name", "name"), ("Category", "category"),
            ("Unit Sale Price", "unit_price"), ("Cost Price", "cost_price"),
            ("Initial Stock", "stock_quantity"), ("Size (e.g. M, L, 32)", "size"),
            ("Color", "color"), ("Description", "description")
        ]

        for label, key in fields:
            tk.Label(self.form_frame, text=label, font=("Arial", 9, "bold"), bg="white").pack(anchor="w", padx=25)
            entry = tk.Entry(self.form_frame, font=("Arial", 11), bg="#f8f9fa", relief="flat", highlightthickness=1)
            entry.pack(fill="x", padx=25, pady=(2, 10))
            self.entries[key] = entry

        # Season Dropdown
        tk.Label(self.form_frame, text="Season", font=("Arial", 9, "bold"), bg="white").pack(anchor="w", padx=25)
        self.season_cb = ttk.Combobox(self.form_frame, values=["Summer", "Winter", "All"], state="readonly", font=("Arial", 10))
        self.season_cb.set("All")
        self.season_cb.pack(fill="x", padx=25, pady=(2, 10))

        # Image Section
        img_btn = tk.Button(self.form_frame, text="UPLOAD IMAGE", command=self.select_image, 
                            bg=self.colors["accent"], fg="white", font=("Arial", 8, "bold"))
        img_btn.pack(pady=5)
        
        self.image_preview = tk.Label(self.form_frame, bg="white", text="No Image Selected", fg="gray")
        self.image_preview.pack(pady=5)

        # Action Buttons
        btn_frame = tk.Frame(self.form_frame, bg="white")
        btn_frame.pack(fill="x", pady=20, padx=25)

        self.add_button = tk.Button(btn_frame, text="ADD ITEM", command=self.add_item, 
                                    bg=self.colors["success"], fg="white", font=("Arial", 10, "bold"), width=15)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_button = tk.Button(btn_frame, text="UPDATE", command=self.update_item, 
                                       state="disabled", bg=self.colors["warning"], font=("Arial", 10, "bold"), width=15)
        self.update_button.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(self.form_frame, text="DELETE ITEM", command=self.delete_item, 
                  bg=self.colors["danger"], fg="white", font=("Arial", 10, "bold")).pack(fill="x", padx=30, pady=5)

        tk.Button(self.form_frame, text="BACK TO DASHBOARD", command=self.go_back, 
                  bg=self.colors["primary"], fg="white", font=("Arial", 10, "bold")).pack(fill="x", padx=30, pady=10)

    # --- FUNCTIONALITY ---

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def perform_search(self):
        term = self.search_ent.get().strip()
        category = self.search_by_var.get()
        results = database.search_items(term, category)
        self.display_results(results)

    def display_results(self, items):
        for i in self.item_tree.get_children():
            self.item_tree.delete(i)
        for item in items:
            self.item_tree.insert("", tk.END, values=(
                item["item_id"], item["name"], item["category"],
                item["unit_price"], item["stock_quantity"],
                item["season"], item["size"], item["color"]
            ))

    def load_items(self):
        self.search_ent.delete(0, tk.END)
        conn = database.get_db_connection()
        items = conn.execute("SELECT * FROM cloth_items").fetchall()
        conn.close()
        self.display_results(items)
        self.clear_form()

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            filename = f"img_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(file_path)}"
            dest_path = os.path.join(UPLOAD_DIR, filename)
            import shutil
            shutil.copyfile(file_path, dest_path)
            self.image_path = dest_path
            self.show_image(dest_path)

    def show_image(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((120, 120))
            img_tk = ImageTk.PhotoImage(img)
            self.image_preview.configure(image=img_tk, text="")
            self.image_preview.image = img_tk
        except:
            self.image_preview.configure(text="Error loading image")

    def on_item_select(self, event):
        selected = self.item_tree.selection()
        if not selected: return
        
        item_data = self.item_tree.item(selected[0])['values']
        item_id = item_data[0]

        conn = database.get_db_connection()
        item = conn.execute("SELECT * FROM cloth_items WHERE item_id = ?", (item_id,)).fetchone()
        conn.close()

        if item:
            self.selected_item_id = item["item_id"]
            for key in self.entries:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, str(item[key] if item[key] is not None else ""))
            
            self.season_cb.set(item["season"])
            self.image_path = item["image_path"]
            if self.image_path and os.path.exists(self.image_path):
                self.show_image(self.image_path)
            else:
                self.image_preview.configure(image="", text="No Image")

            self.add_button.config(state="disabled")
            self.update_button.config(state="normal")

    def add_item(self):
        try:
            v = {k: e.get() for k, e in self.entries.items()}
            database.add_item(v["name"], v["category"], float(v["unit_price"]), float(v["cost_price"]),
                              int(v["stock_quantity"]), self.season_cb.get(), v["size"], v["color"],
                              self.image_path, v["description"])
            messagebox.showinfo("Success", "New item added to inventory.")
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add: {e}")

    def update_item(self):
        try:
            v = {k: e.get() for k, e in self.entries.items()}
            database.update_item(self.selected_item_id, v["name"], v["category"], float(v["unit_price"]),
                                 float(v["cost_price"]), int(v["stock_quantity"]), self.season_cb.get(),
                                 v["size"], v["color"], self.image_path, v["description"])
            messagebox.showinfo("Success", "Item updated successfully.")
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")

    def delete_item(self):
        if self.selected_item_id and messagebox.askyesno("Confirm", "Delete this item permanently?"):
            database.delete_item(self.selected_item_id)
            self.load_items()

    def clear_form(self):
        self.selected_item_id = None
        for e in self.entries.values(): e.delete(0, tk.END)
        self.season_cb.set("All")
        self.image_path = None
        self.image_preview.configure(image="", text="No Image Selected")
        self.add_button.config(state="normal")
        self.update_button.config(state="disabled")

    def go_back(self):
        self.root.destroy()
        from admin_dashboard import AdminDashboard
        root = tk.Tk()
        AdminDashboard(root, {'username': 'admin', 'role': 'Admin'})
        root.mainloop()