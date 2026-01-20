import sqlite3
from datetime import datetime

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect('clothes_db.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key support
    return conn

def init_db():
    """Initializes the database by creating required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Admin', 'User')),
            created_at TEXT NOT NULL
        )
    ''')

    # 2. Create cloth_items table (The Item Master)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cloth_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            unit_price REAL NOT NULL,      -- Selling Price
            cost_price REAL NOT NULL,      -- Buying Price
            stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0),
            season TEXT NOT NULL CHECK(season IN ('Summer', 'Winter', 'All')),
            size TEXT,
            color TEXT,
            image_path TEXT,
            added_at TEXT NOT NULL
        )
    ''')

    # 3. Create Purchases table (Records stock coming IN)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity_purchased INTEGER NOT NULL CHECK(quantity_purchased > 0),
            purchase_date TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES cloth_items(item_id) ON DELETE RESTRICT
        )
    ''')

    # 4. Create Sales table (Records stock going OUT)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity_sold INTEGER NOT NULL CHECK(quantity_sold > 0),
            sale_price REAL NOT NULL,     -- Price at the time of sale
            sale_date TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES cloth_items(item_id) ON DELETE RESTRICT
        )
    ''')

    # Insert default admin user if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role, created_at)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin', 'Admin', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()

# --- User Functions ---

def add_user(username, password, role):
    conn = get_db_connection()
    try:
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute('INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)', 
                     (username, password, role, created_at))
        conn.commit()
    finally:
        conn.close()

def authenticate_user(username, password, role):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', 
                        (username, password, role)).fetchone()
    conn.close()
    return user

# --- Item Management Functions ---

def add_item(name, category, unit_price, cost_price, stock_quantity, season, size, color, image_path=None, description=None):
    conn = get_db_connection()
    added_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        conn.execute('''
            INSERT INTO cloth_items (name, category, unit_price, cost_price, stock_quantity, season, size, color, image_path, description, added_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, unit_price, cost_price, stock_quantity, season, size, color, image_path, description, added_at))
        conn.commit()
    finally:
        conn.close()

def update_item(item_id, name, category, unit_price, cost_price, stock_quantity, season, size, color, image_path=None, description=None):
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE cloth_items
            SET name=?, category=?, unit_price=?, cost_price=?, stock_quantity=?, season=?, size=?, color=?, image_path=?, description=?
            WHERE item_id=?
        ''', (name, category, unit_price, cost_price, stock_quantity, season, size, color, image_path, description, item_id))
        conn.commit()
    finally:
        conn.close()

def delete_item(item_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM cloth_items WHERE item_id = ?', (item_id,))
        conn.commit()
    finally:
        conn.close()

def search_items(search_term, search_by='name'):
    conn = get_db_connection()
    query = f"SELECT * FROM cloth_items WHERE {search_by} LIKE ?"
    items = conn.execute(query, (f'%{search_term}%',)).fetchall()
    conn.close()
    return items

# --- Automated Transaction Functions ---

def record_purchase(item_id, quantity):
    """Automated Purchase: Updates stock based on pre-defined cost_price."""
    conn = get_db_connection()
    cursor = conn.cursor()
    purchase_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        # Record the purchase event
        cursor.execute('INSERT INTO purchases (item_id, quantity_purchased, purchase_date) VALUES (?, ?, ?)', 
                       (item_id, quantity, purchase_date))
        # Update current stock
        cursor.execute('UPDATE cloth_items SET stock_quantity = stock_quantity + ? WHERE item_id = ?', (quantity, item_id))
        conn.commit()
    finally:
        conn.close()

def record_sale(item_id, quantity):
    """Automated Sale: Fetches current unit_price from DB to calculate total."""
    conn = get_db_connection()
    cursor = conn.cursor()
    sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        # Fetch item details (Automated price retrieval)
        item = cursor.execute('SELECT stock_quantity, unit_price FROM cloth_items WHERE item_id = ?', (item_id,)).fetchone()
        
        if not item: raise Exception("Item not found")
        if item['stock_quantity'] < quantity: raise Exception("Insufficient stock")

        # Automatically use the selling price stored in database
        sale_price = item['unit_price']

        cursor.execute('INSERT INTO sales (item_id, quantity_sold, sale_price, sale_date) VALUES (?, ?, ?, ?)', 
                       (item_id, quantity, sale_price, sale_date))
        cursor.execute('UPDATE cloth_items SET stock_quantity = stock_quantity - ? WHERE item_id = ?', (quantity, item_id))
        conn.commit()
    finally:
        conn.close()

# --- Report Functions (Corrected Profit Formulas) ---

def generate_report(report_type, start_date=None, end_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if report_type == 'stock':
        data = cursor.execute('SELECT * FROM cloth_items').fetchall()
        conn.close()
        return data

    start_dt = f"{start_date} 00:00:00" if start_date else "1970-01-01 00:00:00"
    end_dt = f"{end_date} 23:59:59" if end_date else "9999-12-31 23:59:59"

    if report_type == 'sales':
        return cursor.execute('''
            SELECT s.sale_id, s.item_id, i.name, s.quantity_sold, s.sale_price, s.sale_date
            FROM sales s JOIN cloth_items i ON s.item_id = i.item_id
            WHERE s.sale_date BETWEEN ? AND ?
        ''', (start_dt, end_dt)).fetchall()

    elif report_type == 'purchases':
        return cursor.execute('''
            SELECT p.purchase_id, p.item_id, i.name, p.quantity_purchased, i.cost_price, p.purchase_date
            FROM purchases p JOIN cloth_items i ON p.item_id = i.item_id
            WHERE p.purchase_date BETWEEN ? AND ?
        ''', (start_dt, end_dt)).fetchall()

    elif report_type == 'profit':
        # Formula: 
        # Total Revenue = Quantity Sold * Sale Price
        # Total COGS (Cost of Goods Sold) = Quantity Sold * Item Buy Price
        # Profit = Revenue - COGS
        
        cursor.execute('''
            SELECT s.quantity_sold, s.sale_price, i.cost_price
            FROM sales s JOIN cloth_items i ON s.item_id = i.item_id
            WHERE s.sale_date BETWEEN ? AND ?
        ''', (start_dt, end_dt))
        sales_rows = cursor.fetchall()

        total_revenue = sum(row['sale_price'] * row['quantity_sold'] for row in sales_rows)
        total_cogs = sum(row['cost_price'] * row['quantity_sold'] for row in sales_rows)
        net_profit = total_revenue - total_cogs

        # Also calculate total expenditure on new stock (Cash Flow)
        cursor.execute('''
            SELECT p.quantity_purchased, i.cost_price 
            FROM purchases p JOIN cloth_items i ON p.item_id = i.item_id
            WHERE p.purchase_date BETWEEN ? AND ?
        ''', (start_dt, end_dt))
        purch_rows = cursor.fetchall()
        total_purchase_cost = sum(row['cost_price'] * row['quantity_purchased'] for row in purch_rows)

        conn.close()
        return {
            'sales_profit': total_revenue,        # Gross Revenue
            'purchase_profit': total_purchase_cost, # Total Expenditure
            'total_profit': net_profit            # Actual Business Profit
        }

    conn.close()
    return []

if __name__ == '__main__':
    init_db()