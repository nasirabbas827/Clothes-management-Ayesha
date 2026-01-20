import tkinter as tk
from tkinter import ttk, messagebox
from database import search_items, record_sale
from PIL import Image, ImageTk
import os

class UserItemsWindow:
    def __init__(self, root, user_data, parent_root):
        self.root = root
        self.user_data = user_data
        self.parent_root = parent_root
        self.root.title("Clothes Management | Sales Terminal")
        self.root.state('zoomed')
        self.root.configure(bg="#f8f9fa")

        self.colors = {
            "primary": "#2c3e50", "accent": "#3498db",
            "success": "#27ae60", "danger": "#e74c3c",
            "white": "#ffffff", "bg": "#f8f9fa"
        }

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=70)
        header.pack(fill=tk.X)
        tk.Label(header, text="Clothes Management Sales Terminal", font=("Helvetica", 18, "bold"), 
                 fg="white", bg=self.colors["primary"]).pack(side=tk.LEFT, padx=30, pady=15)

        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # LEFT SIDE: Product Catalog
        left_side = tk.Frame(main_container, bg=self.colors["bg"])
        left_side.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Search Bar
        search_card = tk.Frame(left_side, bg="white", padx=15, pady=15, highlightthickness=1, highlightbackground="#e0e0e0")
        search_card.pack(fill=tk.X, pady=(0, 10))
        self.search_var = tk.StringVar()
        tk.Entry(search_card, textvariable=self.search_var, font=("Arial", 11), width=40, bg="#f1f3f4", relief="flat").pack(side=tk.LEFT, padx=10)
        self.search_var.trace_add("write", lambda *args: self.load_items())

        # Treeview
        self.tree = ttk.Treeview(left_side, columns=("ID", "Name", "Category", "Price", "Stock"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

        # RIGHT SIDE: Checkout Sidebar
        right_side = tk.Frame(main_container, bg="white", width=380, highlightthickness=1, highlightbackground="#e0e0e0")
        right_side.pack(side=tk.RIGHT, fill=tk.Y)
        right_side.pack_propagate(False)

        form_frame = tk.Frame(right_side, bg="white", padx=30, pady=30)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Product Info
        tk.Label(form_frame, text="Product ID", font=("Arial", 9), bg="white").pack(anchor="w")
        self.sale_item_id_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.sale_item_id_var, state="readonly", font=("Arial", 12)).pack(fill=tk.X, pady=(2, 15))

        tk.Label(form_frame, text="Unit Price", font=("Arial", 9), bg="white").pack(anchor="w")
        self.sale_price_var = tk.StringVar(value="0.00")
        tk.Entry(form_frame, textvariable=self.sale_price_var, state="readonly", font=("Arial", 12)).pack(fill=tk.X, pady=(2, 15))

        # NEW: View Image Pop-up Button
        self.img_btn = tk.Button(form_frame, text="👁 VIEW PRODUCT IMAGE", font=("Arial", 10, "bold"), 
                                 bg=self.colors["accent"], fg="white", relief="flat", pady=8, 
                                 state="disabled", command=self.show_image_popup)
        self.img_btn.pack(fill=tk.X, pady=(5, 20))

        # Quantity
        tk.Label(form_frame, text="Quantity", font=("Arial", 10, "bold"), bg="white").pack(anchor="w")
        self.sale_quantity_var = tk.StringVar(value="1")
        self.sale_quantity_var.trace_add("write", self.update_total_display)
        tk.Entry(form_frame, textvariable=self.sale_quantity_var, font=("Arial", 14), highlightthickness=1).pack(fill=tk.X, pady=(2, 20))

        # Total
        tk.Label(form_frame, text="GRAND TOTAL", font=("Arial", 10, "bold"), bg="white", fg="#7f8c8d").pack()
        self.total_display_var = tk.StringVar(value="RS 0.00")
        tk.Label(form_frame, textvariable=self.total_display_var, font=("Helvetica", 22, "bold"), bg="white", fg=self.colors["success"]).pack(pady=10)

        # Actions
        tk.Button(form_frame, text="COMPLETE SALE", command=self.sell_item, font=("Arial", 12, "bold"), 
                  bg=self.colors["success"], fg="white", relief="flat", pady=12).pack(fill=tk.X, pady=(20, 10))
        
        tk.Button(form_frame, text="Back", command=self.on_close, bg="#95a5a6", fg="white", relief="flat").pack(fill=tk.X)

        self.current_image_path = None
        self.load_items()

    def show_image_popup(self):
        """Creates a pop-up window to display the image."""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            messagebox.showwarning("Image", "No image file found for this product.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Product Preview")
        popup.geometry("300x300")
        popup.resizable(False, False)
        popup.configure(bg="white")

        try:
            img = Image.open(self.current_image_path).resize((250, 250), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            lbl = tk.Label(popup, image=photo, bg="white")
            lbl.image = photo # Keep reference
            lbl.pack(expand=True)
        except Exception as e:
            tk.Label(popup, text="Error loading image").pack(expand=True)

    def on_item_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        values = self.tree.item(selected[0])['values']
        
        self.sale_item_id_var.set(values[0])
        self.sale_price_var.set(values[3])
        self.update_total_display()

        # Check for image availability
        items = search_items(values[0], 'item_id')
        if items and items[0]['image_path']:
            self.current_image_path = items[0]['image_path']
            self.img_btn.config(state="normal", bg=self.colors["accent"])
        else:
            self.current_image_path = None
            self.img_btn.config(state="disabled", bg="#bdc3c7")

    def update_total_display(self, *args):
        try:
            price = float(self.sale_price_var.get())
            qty = int(self.sale_quantity_var.get()) if self.sale_quantity_var.get().isdigit() else 0
            self.total_display_var.set(f"RS {price * qty:,.2f}")
        except:
            self.total_display_var.set("RS 0.00")

    def load_items(self):
        self.tree.delete(*self.tree.get_children())
        items = search_items(self.search_var.get())
        for item in items:
            self.tree.insert('', tk.END, values=(item['item_id'], item['name'], item['category'], f"{item['unit_price']:.2f}", item['stock_quantity']))

    def sell_item(self):
        try:
            record_sale(int(self.sale_item_id_var.get()), int(self.sale_quantity_var.get()))
            messagebox.showinfo("Success", "Sale Recorded!")
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_close(self):
        self.root.destroy()
        self.parent_root.deiconify()