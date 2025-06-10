import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from fpdf import FPDF
import os
from datetime import datetime
import webbrowser
import tkinter.font as tkFont
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ========== Utility Functions ==========
def load_inventory():
    try:
        df = pd.read_csv("inventory.csv")
        # Ensure all required columns exist
        required_cols = ["product_id", "name", "brand", "category", "quantity", "price"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        return df[required_cols]
    except Exception:
        return pd.DataFrame(columns=["product_id", "name", "brand", "category", "quantity", "price"])

def save_inventory(df):
    df.to_csv("inventory.csv", index=False)

def generate_invoice(items, total, customer_name="Customer", discount=0):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "Shahbaz Munir ELECTRO Hub", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 6, "Arifwala road main bazzar, Qabula", ln=True, align='C')
    pdf.cell(190, 6, "Phone: 0300-0000000 | Email: shahbazmunir@email.com", ln=True, align='C')
    pdf.ln(10)

    invoice_no = datetime.now().strftime('%Y%m%d%H%M%S')[-6:]
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 6, f"Invoice No: INV-{invoice_no}", ln=False)
    pdf.cell(95, 6, f"Invoice Date: {datetime.now().strftime('%d-%b-%Y')}", ln=True)

    pdf.set_font("Arial", '', 11)
    pdf.cell(95, 6, "From:", ln=False)
    pdf.cell(95, 6, "Bill To:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 6, "Shahbaz Munir ELECTRO HUB", ln=False)
    pdf.cell(95, 6, customer_name, ln=True)  # <-- yahan customer ka naam
    pdf.cell(95, 6, "Arifwala road main bazzar, Qabula", ln=False)
    pdf.cell(95, 6, "", ln=True)
    pdf.ln(8)

    # Table Header
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(70, 8, "Description", 1, 0, 'C', 1)
    pdf.cell(25, 8, "Qty", 1, 0, 'C', 1)
    pdf.cell(45, 8, "Unit Price (Rs)", 1, 0, 'C', 1)
    pdf.cell(45, 8, "Amount (Rs)", 1, 1, 'C', 1)

    pdf.set_font("Arial", '', 10)
    for item in items:
        name = item['name'][:30]
        qty = item['quantity']
        price = item['price']
        amount = qty * price
        pdf.cell(70, 8, name, 1)
        pdf.cell(25, 8, str(qty), 1, 0, 'C')
        pdf.cell(45, 8, f"{price:.2f}", 1, 0, 'R')
        pdf.cell(45, 8, f"{amount:.2f}", 1, 1, 'R')

    pdf.set_font("Arial", 'B', 11)
    pdf.cell(140, 8, "Total Amount", 1)
    pdf.cell(45, 8, f"Rs {total:.2f}", 1, 1, 'R')

    if discount > 0:
        pdf.set_font("Arial", '', 11)
        pdf.cell(140, 8, "Discount", 1)
        pdf.cell(45, 8, f"- Rs {discount:.2f}", 1, 1, 'R')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(140, 8, "Grand Total", 1)
        pdf.cell(45, 8, f"Rs {total-discount:.2f}", 1, 1, 'R')

    pdf.ln(10)
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 6, "Payment Instructions:", ln=True)
    pdf.cell(190, 6, "Please make the payment by the due date.", ln=True)
    pdf.cell(190, 6, "Authorized Signature:", ln=True)
    pdf.ln(15)
    pdf.cell(190, 6, "_____________________________", ln=True)

    filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    try:
        pdf.output(filename)
    except UnicodeEncodeError:
        safe_filename = filename.encode('utf-8', 'replace').decode('utf-8')
        pdf.output(safe_filename)
        filename = safe_filename
    return filename

def save_sale(items, total, customer_name, discount):
    # Convert all items to pure Python types
    def to_py(obj):
        if isinstance(obj, dict):
            return {k: to_py(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_py(x) for x in obj]
        elif hasattr(obj, 'item'):
            return obj.item()
        else:
            return obj

    items_py = to_py(items)

    df = pd.DataFrame([{
        "date": datetime.now().strftime('%Y-%m-%d'),
        "time": datetime.now().strftime('%H:%M:%S'),
        "customer": customer_name,
        "items": json.dumps(items_py),  # Save as JSON string
        "total": float(total),
        "discount": float(discount),
        "grand_total": float(total) - float(discount)
    }])
    if os.path.exists("sales.csv"):
        df.to_csv("sales.csv", mode='a', header=False, index=False)
    else:
        df.to_csv("sales.csv", mode='w', header=True, index=False)

# main program
class ElectronicsShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛒 Electronics Shop Manager")
        self.df = load_inventory()
        self.bill_items = []

        # Set window size and center
        w, h = 1200, 700
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.configure(bg="#f4f6fa")

        # Custom fonts
        heading_font = tkFont.Font(family="Helvetica", size=22, weight="bold")
        button_font = tkFont.Font(family="Helvetica", size=11, weight="bold")
        label_font = tkFont.Font(family="Helvetica", size=12)
        table_font = tkFont.Font(family="Segoe UI", size=13)

        # === Heading ===
        heading = tk.Label(root, text="ELECTRO HUB - Inventory Manager", font=heading_font, bg="#2d4059", fg="#fff", pady=12)
        heading.pack(fill="x", pady=(0, 8))

        # Custom style for hover effect on buttons
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TButton",
            font=button_font,
            background="#ea5455",
            foreground="#fff",
            borderwidth=0,
            focusthickness=3,
            focuscolor='none',
            padding=8
        )
        style.map("Custom.TButton",
            background=[('active', '#ff7675'), ('!active', '#ea5455')],
            foreground=[('active', '#fff'), ('!active', '#fff')]
        )

        # === Top Frame with buttons ===
        top_frame = tk.Frame(root, bg="#f4f6fa")
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Button(top_frame, text="➕ Add Product", command=self.add_product, style="Custom.TButton").pack(side="left", padx=6)
        ttk.Button(top_frame, text="✏️ Edit Product", command=self.edit_product, style="Custom.TButton").pack(side="left", padx=6)
        ttk.Button(top_frame, text="🗑️ Delete Product", command=self.delete_product, style="Custom.TButton").pack(side="left", padx=6)
        ttk.Button(top_frame, text="🛒 Add To Bill", command=self.add_to_bill, style="Custom.TButton").pack(side="left", padx=6)
        ttk.Button(top_frame, text="🧾 Make Bill", command=self.make_bill, style="Custom.TButton").pack(side="left", padx=6)
        ttk.Button(top_frame, text="🔁 Refresh", command=self.refresh_table, style="Custom.TButton").pack(side="left", padx=6)
        ttk.Button(top_frame, text="📈 Sales Analytics", command=self.show_sales_analytics, style="Custom.TButton").pack(side="left", padx=6)

        # === Search and Sort Frame ===
        filter_frame = tk.Frame(root, bg="#f4f6fa")
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Search:", font=label_font, bg="#f4f6fa").grid(row=0, column=0, padx=(10, 2), pady=8, sticky="e")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.refresh_table())
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var, font=label_font, width=28, bd=2, relief="groove")
        search_entry.grid(row=0, column=1, padx=(0, 18), pady=8, sticky="w")

        tk.Label(filter_frame, text="Sort by:", font=label_font, bg="#f4f6fa").grid(row=0, column=2, padx=(10, 2), pady=8, sticky="e")
        self.sort_col_var = tk.StringVar(value="product_id")
        self.sort_order_var = tk.StringVar(value="Ascending")
        cols = list(self.df.columns)
        sort_col_menu = tk.OptionMenu(filter_frame, self.sort_col_var, *cols, command=lambda _: self.refresh_table())
        sort_col_menu.config(font=label_font, width=14, bg="#fff", bd=1, highlightthickness=1, relief="groove")
        sort_col_menu.grid(row=0, column=3, padx=(0, 10), pady=8, sticky="w")

        sort_order_menu = tk.OptionMenu(filter_frame, self.sort_order_var, "Ascending", "Descending", command=lambda _: self.refresh_table())
        sort_order_menu.config(font=label_font, width=12, bg="#fff", bd=1, highlightthickness=1, relief="groove")
        sort_order_menu.grid(row=0, column=4, padx=(0, 10), pady=8, sticky="w")

        # Add a stretchable empty column for better spacing
        filter_frame.grid_columnconfigure(5, weight=1)

        # === Table Frame with border and background ===
        table_outer = tk.Frame(root, bg="#2d4059", bd=2, relief="ridge", highlightthickness=2, highlightbackground="#2d4059")
        table_outer.pack(fill="both", expand=True, padx=15, pady=10)
        table_frame = tk.Frame(table_outer, bg="#fff", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            font=table_font,
            rowheight=38,
            background="#fff",
            # fieldbackground="#fff",
            borderwidth=2,      # Thicker border
            relief="solid"
        )
        style.configure("Treeview.Heading",
            font=("Segoe UI", 14, "bold"),
            background="#2d4059",
            foreground="#fff",
            borderwidth=2,
            relief="solid"
        )
        style.map("Treeview.Heading",
            background=[('active', "#ea5455"), ('!active', "#2d4059")],
            foreground=[('active', '#fff'), ('!active', '#fff')]
        )
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        self.tree = ttk.Treeview(
            table_frame,
            columns=list(self.df.columns),
            show="headings",
            selectmode="browse",
            height=14,
            style="Treeview"
        )
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # === Status Bar ===
        self.status_var = tk.StringVar()
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w", font=("Segoe UI", 10), bg="#32314f")
        status_bar.pack(side="bottom", fill="x")
        self.set_status("Welcome to Electro Hub Inventory Manager!")

        self.refresh_table()

    def set_status(self, msg):
        self.status_var.set(msg)

    # Refresh table with search & sort
    def refresh_table(self):
        self.df = load_inventory()
        search_text = self.search_var.get().lower()
        df_filtered = self.df[
            self.df.apply(lambda row:
                          search_text in str(row["product_id"]).lower()
                          or search_text in str(row["name"]).lower()
                          or search_text in str(row["brand"]).lower()
                          or search_text in str(row["category"]).lower(),
                          axis=1)   
        ]

        sort_col = self.sort_col_var.get()
        ascending = self.sort_order_var.get() == "Ascending"

        df_filtered = df_filtered.sort_values(by=sort_col, ascending=ascending)

        self.tree.delete(*self.tree.get_children())
        for _, row in df_filtered.iterrows():
            self.tree.insert("", "end", values=list(row))

        # Scroll to last item
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])

    def add_product(self):
        win = tk.Toplevel(self.root)
        win.title("Add Product")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)
        font = ("Segoe UI", 12)

        # Center the window on the parent
        win.update_idletasks()
        w, h = 400, 480
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

        win.lift()
        win.focus_force()
        win.attributes('-topmost', True)
        win.after(10, lambda: win.attributes('-topmost', False))

        frame = tk.Frame(win)
        frame.pack(expand=True, fill="both", pady=10)

        tk.Label(frame, text="Product ID:", font=font).pack(pady=(10, 2))
        pid_var = tk.StringVar()
        pid_entry = tk.Entry(frame, textvariable=pid_var, font=font)
        pid_entry.pack()

        tk.Label(frame, text="Name:", font=font).pack(pady=(10, 2))
        name_var = tk.StringVar()
        name_entry = tk.Entry(frame, textvariable=name_var, font=font)
        name_entry.pack()

        tk.Label(frame, text="Brand:", font=font).pack(pady=(10, 2))
        brand_var = tk.StringVar()
        brand_entry = tk.Entry(frame, textvariable=brand_var, font=font)
        brand_entry.pack()

        tk.Label(frame, text="Category:", font=font).pack(pady=(10, 2))
        cat_var = tk.StringVar()
        cat_entry = tk.Entry(frame, textvariable=cat_var, font=font)
        cat_entry.pack()

        tk.Label(frame, text="Quantity:", font=font).pack(pady=(10, 2))
        qty_var = tk.StringVar()
        qty_entry = tk.Entry(frame, textvariable=qty_var, font=font)
        qty_entry.pack()

        tk.Label(frame, text="Price:", font=font).pack(pady=(10, 2))
        price_var = tk.StringVar()
        price_entry = tk.Entry(frame, textvariable=price_var, font=font)
        price_entry.pack()

        def submit(event=None):
            try:
                pid = int(pid_var.get())
                if pid in self.df['product_id'].values:
                    messagebox.showerror("Error", "Product ID already exists!", parent=win)
                    return
                name = name_var.get().strip()
                brand = brand_var.get().strip()
                cat = cat_var.get().strip()
                qty = int(qty_var.get())
                price = float(price_var.get())
                if not name or not brand or not cat:
                    messagebox.showerror("Error", "All fields are required!", parent=win)
                    return
                new_row = pd.DataFrame([{
                    "product_id": pid,
                    "name": name,
                    "brand": brand,
                    "category": cat,
                    "quantity": qty,
                    "price": price
                }])
                self.df = pd.concat([self.df, new_row], ignore_index=True)
                save_inventory(self.df)
                self.refresh_table()
                win.destroy()
                messagebox.showinfo("Success", "Product added successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input! {e}", parent=win)

        def close(event=None):
            win.destroy()

        add_btn = tk.Button(frame, text="Add Product", font=font, bg="#2d4059", fg="#fff", command=submit)
        add_btn.pack(pady=18)

        # Bind Enter to submit and Escape to close
        win.bind('<Return>', submit)
        win.bind('<Escape>', close)
        pid_entry.focus_set()

        win.wait_window()
    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to edit!")
            return
        item = self.tree.item(selected)
        pid = item['values'][0]

        product = self.df[self.df["product_id"] == pid].iloc[0]

        def submit():
            try:
                name = name_var.get().strip()
                brand = brand_var.get().strip()
                cat = cat_var.get().strip()
                qty = int(qty_var.get())
                price = float(price_var.get())
                if not name or not brand or not cat:
                    messagebox.showerror("Error", "All fields are required!", parent=win)
                    return
                self.df.loc[self.df["product_id"] == pid, ["name", "brand", "category", "quantity", "price"]] = [name, brand, cat, qty, price]
                save_inventory(self.df)
                self.refresh_table()
                win.destroy()
                messagebox.showinfo("Success", "Product edited successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input! {e}", parent=win)

        win = tk.Toplevel(self.root)
        win.title("Edit Product")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)
        font = ("Segoe UI", 12)

        # Center the window on the parent
        win.update_idletasks()
        w, h = 400, 420
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

        win.lift()
        win.focus_force()
        win.attributes('-topmost', True)
        win.after(10, lambda: win.attributes('-topmost', False))

        frame = tk.Frame(win)
        frame.pack(expand=True, fill="both", pady=10)

        tk.Label(frame, text="Name:", font=font).pack(pady=(10, 2))
        name_var = tk.StringVar(value=product['name'])
        tk.Entry(frame, textvariable=name_var, font=font).pack()

        tk.Label(frame, text="Brand:", font=font).pack(pady=(10, 2))
        brand_var = tk.StringVar(value=product['brand'])
        tk.Entry(frame, textvariable=brand_var, font=font).pack()

        tk.Label(frame, text="Category:", font=font).pack(pady=(10, 2))
        cat_var = tk.StringVar(value=product['category'])
        tk.Entry(frame, textvariable=cat_var, font=font).pack()

        tk.Label(frame, text="Quantity:", font=font).pack(pady=(10, 2))
        qty_var = tk.StringVar(value=str(product['quantity']))
        tk.Entry(frame, textvariable=qty_var, font=font).pack()

        tk.Label(frame, text="Price:", font=font).pack(pady=(10, 2))
        price_var = tk.StringVar(value=str(product['price']))
        tk.Entry(frame, textvariable=price_var, font=font).pack()

        tk.Button(frame, text="Update Product", font=font, bg="#2d4059", fg="#fff", command=submit).pack(pady=18)

        win.wait_window()

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to delete!")
            return
        item = self.tree.item(selected)
        pid = item['values'][0]

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            self.df = self.df[self.df["product_id"] != pid]
            save_inventory(self.df)
            self.refresh_table()
            messagebox.showinfo("Deleted", "Product deleted successfully.")

    def add_to_bill(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to add to bill!")
            return
        item = self.tree.item(selected)
        pid = item['values'][0]

        product = self.df[self.df["product_id"] == pid].iloc[0]

        def submit(event=None):
            try:
                qty = int(qty_var.get())
                if qty > product['quantity']:
                    messagebox.showerror("Error", "Quantity exceeds available stock!", parent=win)
                    return
                # Check if already in bill, update quantity if so
                for bill_item in self.bill_items:
                    if bill_item['product_id'] == pid:
                        if bill_item['quantity'] + qty > product['quantity']:
                            messagebox.showerror("Error", "Total quantity in bill exceeds available stock!", parent=win)
                            return
                        bill_item['quantity'] += qty
                        bill_item['total'] = bill_item['quantity'] * bill_item['price']
                        messagebox.showinfo("Updated", f"Updated quantity for {product['name']} in bill.", parent=win)
                        win.destroy()
                        return
                else:
                    total_price = qty * product['price']
                    self.bill_items.append({
                        "product_id": pid,
                        "name": product['name'],
                        "quantity": qty,
                        "price": product['price'],
                        "total": total_price
                    })
                    messagebox.showinfo("Added", f"Added {qty} x {product['name']} to bill.", parent=win)
                    win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid quantity! {e}", parent=win)

        def close(event=None):
            win.destroy()

        win = tk.Toplevel(self.root)
        win.title("Add To Bill")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)
        font = ("Segoe UI", 13)

        # Center the window on the parent
        win.update_idletasks()
        w, h = 400, 240
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

        win.lift()
        win.focus_force()
        win.attributes('-topmost', True)
        win.after(10, lambda: win.attributes('-topmost', False))

        frame = tk.Frame(win)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text=f"Product: {product['name']}", font=(font[0], font[1]+1, "bold")).pack(pady=(0, 8))
        tk.Label(frame, text=f"Available: {product['quantity']}", font=font).pack(pady=(0, 12))

        tk.Label(frame, text="Enter Quantity:", font=font).pack()
        qty_var = tk.StringVar()
        qty_entry = tk.Entry(frame, textvariable=qty_var, font=font, width=15, justify="center")
        qty_entry.pack(pady=(5, 15))

        add_btn = tk.Button(frame, text="Add To Bill", font=font, bg="#2d4059", fg="#fff", command=submit)
        add_btn.pack(pady=8)

        win.bind('<Return>', submit)
        win.bind('<Escape>', close)
        qty_entry.focus_set()

        win.wait_window()

    
    def make_bill(self):
        if not self.bill_items:
            messagebox.showwarning("Warning", "No items in bill!")
            return

        # --- Bill Preview/Edit Dialog ---
        dialog = tk.Toplevel(self.root)
        dialog.title("Preview & Edit Bill")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        font = ("Segoe UI", 12)

        # Bill Items Table
        columns = ("Product", "Qty", "Price", "Total", "Edit", "Delete")
        tree = ttk.Treeview(dialog, columns=columns, show="headings", height=8)
        for col in columns[:-2]:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="center")
        tree.column("Product", width=180)
        tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Populate bill items
        def refresh_tree():
            tree.delete(*tree.get_children())
            for idx, item in enumerate(self.bill_items):
                tree.insert("", "end", iid=idx, values=(
                    item['name'], item['quantity'], f"{item['price']:.2f}", f"{item['total']:.2f}", "Edit", "Delete"
                ))

        refresh_tree()

        # Edit/Delete actions
        def on_tree_click(event):
            item_id = tree.identify_row(event.y)
            col = tree.identify_column(event.x)
            if not item_id:
                return
            idx = int(item_id)
            if col == "#5":  # Edit
                edit_bill_item(idx)
            elif col == "#6":  # Delete
                del self.bill_items[idx]
                refresh_tree()

        tree.bind("<Button-1>", on_tree_click)

        # Edit bill item dialog
        def edit_bill_item(idx):
            item = self.bill_items[idx]
            win = tk.Toplevel(dialog)
            win.title("Edit Bill Item")
            win.transient(dialog)
            win.grab_set()
            win.resizable(False, False)
            tk.Label(win, text=f"Product: {item['name']}", font=font).pack(pady=(10, 2))
            qty_var = tk.StringVar(value=str(item['quantity']))
            tk.Label(win, text="Quantity:", font=font).pack()
            tk.Entry(win, textvariable=qty_var, font=font).pack(pady=(0, 10))
            def save_edit():
                try:
                    qty = int(qty_var.get())
                    if qty < 1:
                        raise ValueError
                    # Check stock
                    stock = int(self.df[self.df["product_id"] == item['product_id']].iloc[0]['quantity'])
                    if qty > stock:
                        messagebox.showerror("Error", "Quantity exceeds available stock!", parent=win)
                        return
                    self.bill_items[idx]['quantity'] = qty
                    self.bill_items[idx]['total'] = qty * self.bill_items[idx]['price']
                    refresh_tree()
                    win.destroy()
                except Exception:
                    messagebox.showerror("Error", "Invalid quantity!", parent=win)
            tk.Button(win, text="Save", font=font, command=save_edit).pack(pady=10)
            win.wait_window()

        # Customer Name & Discount
        tk.Label(dialog, text="Customer Name:", font=font).grid(row=1, column=0, padx=10, pady=(8, 2), sticky="e")
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, font=font, width=18).grid(row=1, column=1, pady=(8, 2), sticky="w")

        tk.Label(dialog, text="Discount (Rs):", font=font).grid(row=2, column=0, padx=10, pady=(2, 10), sticky="e")
        discount_var = tk.StringVar(value="0")
        tk.Entry(dialog, textvariable=discount_var, font=font, width=10).grid(row=2, column=1, pady=(2, 10), sticky="w")

        # Generate Invoice Button
        def submit_bill():
            try:
                customer_name = name_var.get().strip() or "Customer"
                try:
                    discount = float(discount_var.get())
                    if discount < 0:
                        raise ValueError
                except Exception:
                    messagebox.showerror("Error", "Discount must be a non-negative number!", parent=dialog)
                    return

                total_amount = sum(item['total'] for item in self.bill_items)
                invoice_file = generate_invoice(self.bill_items, total_amount, customer_name, discount)
                save_sale(self.bill_items, total_amount, customer_name, discount)

                # Update stock in inventory
                for item in self.bill_items:
                    idx = self.df.index[self.df["product_id"] == item['product_id']][0]
                    self.df.at[idx, "quantity"] -= item['quantity']
                save_inventory(self.df)
                self.bill_items.clear()
                self.refresh_table()

                messagebox.showinfo("Invoice Generated", f"Invoice saved to:\n{invoice_file}")
                webbrowser.open_new_tab(invoice_file)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Exception: {e}", parent=dialog)

        tk.Button(dialog, text="Generate Invoice", font=font, bg="#2d4059", fg="#fff", command=submit_bill).grid(row=3, column=0, columnspan=2, pady=(0, 18))

        dialog.wait_window()

    def show_sales_analytics(self):
        win = tk.Toplevel(self.root)
        win.title("Sales Analytics")
        win.geometry("700x500")
        font = ("Segoe UI", 12)

        # Date filter
        tk.Label(win, text="From (YYYY-MM-DD):", font=font).pack(pady=(10,2))
        from_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-01'))
        tk.Entry(win, textvariable=from_var, font=font).pack()

        tk.Label(win, text="To (YYYY-MM-DD):", font=font).pack(pady=(10,2))
        to_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        tk.Entry(win, textvariable=to_var, font=font).pack()

        def analyze():
            if not os.path.exists("sales.csv"):
                messagebox.showinfo("No Data", "No sales data found.", parent=win)
                return
            df = pd.read_csv("sales.csv")
            df['date'] = pd.to_datetime(df['date'])
            try:
                from_date = pd.to_datetime(from_var.get())
                to_date = pd.to_datetime(to_var.get())
            except:
                messagebox.showerror("Error", "Invalid date format!", parent=win)
                return
            mask = (df['date'] >= from_date) & (df['date'] <= to_date)
            df = df[mask]
            if df.empty:
                messagebox.showinfo("No Data", "No sales in this period.", parent=win)
                return

            # Total sales
            total_sales = df['grand_total'].sum()
            tk.Label(win, text=f"Total Sales: Rs {total_sales:.2f}", font=(font[0], font[1]+2, "bold")).pack(pady=8)

            # Product-wise sales
            all_items = []
            for items_json in df['items']:
                items = json.loads(items_json.replace("'", '"'))
                all_items.extend(items)
            items_df = pd.DataFrame(all_items)
            prod_sales = items_df.groupby('name')['quantity'].sum().sort_values(ascending=True)  # ascending for horizontal

            # Remove old graph if any
            for widget in win.pack_slaves():
                if isinstance(widget, FigureCanvasTkAgg):
                    widget.get_tk_widget().destroy()

            # Plot (horizontal bar, dynamic height)
            n = len(prod_sales)
            fig_height = max(3, n * 0.5)
            fig, ax = plt.subplots(figsize=(8, fig_height))
            prod_sales.plot(kind='barh', ax=ax, color="#ea5455")
            ax.set_xlabel("Quantity Sold")
            ax.set_title("Top Selling Products")
            plt.tight_layout()

            # Scrollable frame for graph
            canvas_frame = tk.Frame(win)
            canvas_frame.pack(fill="both", expand=True, pady=10)
            canvas = tk.Canvas(canvas_frame, height=min(400, fig_height*100))
            scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            inner_frame = tk.Frame(canvas)
            canvas.create_window((0,0), window=inner_frame, anchor="nw")

            fig_canvas = FigureCanvasTkAgg(fig, master=inner_frame)
            fig_canvas.draw()
            fig_canvas.get_tk_widget().pack(fill="both", expand=True)

            # Update scrollregion
            inner_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        tk.Button(win, text="Show Analytics", font=font, bg="#2d4059", fg="#fff", command=analyze).pack(pady=12)

# ========== Main Application ==========




if __name__ == "__main__":
    root = tk.Tk()
    app = ElectronicsShopApp(root)
    root.mainloop()
